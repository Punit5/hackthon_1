print('[DEBUG] main.py started')
import json
import decimal
from data import get_clients
from message_generator import calculate_progress_percent, detect_progress_change, generate_message

def convert_decimals(obj):
    if isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    else:
        return obj

def main():
    try:
        print('[DEBUG] Starting main logic')
        clients_data = get_clients()
        print(f'[DEBUG] Retrieved {len(clients_data)} clients from DB')
        for client in clients_data:
            progress_percent = calculate_progress_percent(client["current_value"], client["goal_amount"])
            progress_change = detect_progress_change(client["current_value"], client["last_month_value"])
            message = generate_message(client, progress_percent, progress_change)
            output = {
                "client_name": client["client_name"],
                "goal_type": client["goal_type"],
                "progress_percent": progress_percent,
                "progress_change": progress_change,
                "message": message
            }
            print(json.dumps(convert_decimals(output), ensure_ascii=False, indent=2))
    except Exception as e:
        print(f'[ERROR] Exception in main: {e}')

if __name__ == "__main__":
    main() 