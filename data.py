import os
import time
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'investment_db')
DB_USER = os.getenv('DB_USER', 'user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def get_clients():
    engine = create_engine(DATABASE_URL)
    max_attempts = 30  # Try for up to 90 seconds
    for attempt in range(max_attempts):
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT client_name, goal_type, goal_amount, current_value, last_month_value, last_message_sent, created_at FROM clients WHERE last_message_sent IS NULL"))
                clients = [dict(row._mapping) for row in result]
            return clients
        except OperationalError as e:
            print(f"[DB WAIT] Database not ready, retrying ({attempt+1}/{max_attempts})...")
            time.sleep(3)
    raise Exception("Could not connect to the database after several attempts.")

clients_data = [
    {
        "client_name": "Jane Doe",
        "goal_type": "Retirement",
        "goal_amount": 100000,
        "current_value": 72000,
        "last_month_value": 72000,
        "last_message_sent": "Hi Jane 👋, you're at 72% of your retirement goal! 🔥 Keep going strong!"
    },
    # Add more clients as needed
] 