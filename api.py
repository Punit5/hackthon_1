from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
import os
import decimal
from message_generator import calculate_progress_percent, detect_progress_change, generate_message
from pydantic import BaseModel, Field
import openai
from dotenv import load_dotenv
from langchain_rag import langchain_ai_chat
from send_sms import send_sms

# Load environment variables from .env
load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'investment_db')
DB_USER = os.getenv('DB_USER', 'user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Azure OpenAI config from environment
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_VERSION = os.getenv("AZURE_OPENAI_VERSION", "2023-05-15")

openai.api_type = "azure"
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_version = AZURE_OPENAI_VERSION
openai.api_key = AZURE_OPENAI_KEY

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def convert_decimals(obj):
    if isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    else:
        return obj

@app.get("/clients")
def get_clients():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, client_name FROM clients ORDER BY client_name"))
        clients = [dict(row._mapping) for row in result]
    return convert_decimals(clients)

@app.get("/clients/{client_id}/all-goal-history")
def get_all_goal_history(client_id: int):
    def is_goal_on_track(current_amount, monthly_contribution, withdrawal_period_months, expected_return_rate, goal_amount):
        r = expected_return_rate / 12
        n = withdrawal_period_months
        P = current_amount
        PMT = monthly_contribution
        if r == 0:
            future_value = P + PMT * n
        else:
            future_value = P * (1 + r) ** n + PMT * (((1 + r) ** n - 1) / r)
        return future_value >= goal_amount

    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Get all goals for the client, including new fields
        goals_result = conn.execute(text("""
            SELECT id, goal_type, goal_amount, initial_amount, current_amount, monthly_contribution, withdrawal_period_months, expected_return_rate
            FROM goals
            WHERE client_id = :client_id
            ORDER BY goal_type
        """), {"client_id": client_id})
        goals = [dict(row._mapping) for row in goals_result]
        # For each goal, get its history and calculate on_track
        for goal in goals:
            history_result = conn.execute(text("""
                SELECT goal_amount, current_amount, last_message_sent, created_at
                FROM goal_history
                WHERE goal_id = :goal_id
                ORDER BY created_at
            """), {"goal_id": goal["id"]})
            goal["history"] = [dict(row._mapping) for row in history_result]
            goal["on_track"] = is_goal_on_track(
                goal["current_amount"],
                goal["monthly_contribution"],
                goal["withdrawal_period_months"],
                goal["expected_return_rate"],
                goal["goal_amount"]
            )
    if not goals:
        raise HTTPException(status_code=404, detail="No goals found for this client.")
    return convert_decimals(goals)

class UpdateGoalAmountRequest(BaseModel):
    client_id: int
    goal_id: int
    current_amount: float
    send_sms: bool = False  # Optional parameter, default False

@app.post("/update-goal-amount")
async def update_goal_amount(req: UpdateGoalAmountRequest):
    engine = create_engine(DATABASE_URL)
    with engine.begin() as conn:
        # 1. Validate goal and client
        goal_result = conn.execute(text("""
            SELECT g.id, g.goal_amount, g.current_amount, g.goal_type, g.client_id, c.client_name
            FROM goals g
            JOIN clients c ON g.client_id = c.id
            WHERE g.id = :goal_id AND g.client_id = :client_id
        """), {"goal_id": req.goal_id, "client_id": req.client_id})
        goal = goal_result.fetchone()
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found for this client.")
        # 2. Calculate progress and change
        progress_percent = calculate_progress_percent(req.current_amount, float(goal.goal_amount))
        progress_change = detect_progress_change(float(req.current_amount), float(goal.current_amount))
        client_dict = {
            "client_name": goal.client_name,
            "goal_type": goal.goal_type,
            "goal_amount": float(goal.goal_amount),
            "current_value": float(req.current_amount),
            "last_month_value": float(goal.current_amount),
            "last_message_sent": None
        }
        message = generate_message(client_dict, progress_percent, progress_change)
        # 3. Update the goal's current_amount
        conn.execute(text("UPDATE goals SET current_amount = :current_amount WHERE id = :goal_id"), {"current_amount": req.current_amount, "goal_id": req.goal_id})
        # 4. Insert into goal_history with the generated message
        conn.execute(text("""
            INSERT INTO goal_history (goal_id, goal_amount, current_amount, last_message_sent, created_at)
            VALUES (:goal_id, :goal_amount, :current_amount, :last_message_sent, NOW())
        """), {
            "goal_id": req.goal_id,
            "goal_amount": goal.goal_amount,
            "current_amount": req.current_amount,
            "last_message_sent": message
        })
    sms_results = []
    if req.send_sms:
        numbers = phone_numbers_cache.get("numbers", [])
        for num in numbers:
            try:
                sid = send_sms(num, message)
                sms_results.append({"number": num, "status": "sent", "sid": sid})
            except Exception as e:
                sms_results.append({"number": num, "status": "failed", "error": str(e)})
    return {
        "message": "Goal updated and history entry created.",
        "motivational_message": message,
        "sms_results": sms_results if req.send_sms else None
    }

class ChatRequest(BaseModel):
    messages: list

@app.post("/api/ai-chat")
def ai_chat(req: ChatRequest):
    answer, sources = langchain_ai_chat(req.messages)
    print("[LANGCHAIN RAG SOURCES]:", sources)
    return {"reply": answer}

# Local cache for phone numbers
phone_numbers_cache = {}

class PhoneNumbersRequest(BaseModel):
    numbers: list[str] = Field(
        ..., 
        example=["+1234567890", "+1987654321", "+1123456789"]
    )

@app.post("/phone-numbers")
def store_phone_numbers(req: PhoneNumbersRequest):
    # Store the numbers in a global cache, override previous
    phone_numbers_cache["numbers"] = req.numbers
    return {"message": "Phone numbers stored.", "count": len(req.numbers)}

@app.get("/phone-numbers")
def get_phone_numbers():
    # Return the current list of phone numbers
    return {"numbers": phone_numbers_cache.get("numbers", [])} 