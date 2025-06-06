# WARNING: This will send a real SMS and use your Twilio credentials. Only use with valid numbers and credentials.
from send_sms import send_sms

if __name__ == "__main__":
    # Replace with a real phone number for testing
    test_number = "+17788463209"
    test_message = "🎉 Congrats! You’re one step closer to your savings goal! 💰 Keep saving and let’s make those dreams a reality! 🌈✨. This is a test message from Goal Pulse!"
    sid = send_sms(test_number, test_message)
    print(f"Message sent! SID: {sid}") 