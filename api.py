from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
import os
import decimal

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'investment_db')
DB_USER = os.getenv('DB_USER', 'user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

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
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Get all goals for the client
        goals_result = conn.execute(text("""
            SELECT id, goal_type, goal_amount, initial_amount, current_amount
            FROM goals
            WHERE client_id = :client_id
            ORDER BY goal_type
        """), {"client_id": client_id})
        goals = [dict(row._mapping) for row in goals_result]
        # For each goal, get its history
        for goal in goals:
            history_result = conn.execute(text("""
                SELECT goal_amount, current_amount, last_message_sent, created_at
                FROM goal_history
                WHERE goal_id = :goal_id
                ORDER BY created_at
            """), {"goal_id": goal["id"]})
            goal["history"] = [dict(row._mapping) for row in history_result]
    if not goals:
        raise HTTPException(status_code=404, detail="No goals found for this client.")
    return convert_decimals(goals) 