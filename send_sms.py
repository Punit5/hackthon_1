from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
MESSAGING_SERVICE_SID = os.getenv("MESSAGING_SERVICE_SID")

def send_sms(to_num, body):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    message = client.messages.create(
        to=to_num,
        messaging_service_sid=MESSAGING_SERVICE_SID,
        body=body
    )
    return message.sid 