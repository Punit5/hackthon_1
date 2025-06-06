import random
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

try:
    import openai
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
    AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    AZURE_OPENAI_VERSION = os.getenv("AZURE_OPENAI_VERSION", "2023-05-15")
    print("[DEBUG] Azure OpenAI Key Loaded:", bool(AZURE_OPENAI_KEY))
    OPENAI_AVAILABLE = AZURE_OPENAI_KEY is not None and AZURE_OPENAI_ENDPOINT is not None and AZURE_OPENAI_DEPLOYMENT is not None
    if OPENAI_AVAILABLE:
        openai.api_type = "azure"
        openai.api_base = AZURE_OPENAI_ENDPOINT
        openai.api_version = AZURE_OPENAI_VERSION
        openai.api_key = AZURE_OPENAI_KEY
except ImportError:
    print("[DEBUG] OpenAI import failed.")
    OPENAI_AVAILABLE = False

def calculate_progress_percent(current_value, goal_amount):
    return round((current_value / goal_amount) * 100, 1)

def detect_progress_change(current_value, last_month_value):
    if current_value > last_month_value:
        return "increased"
    elif current_value == last_month_value:
        return "same"
    else:
        return "decreased"

def get_openai_message(client, progress_percent, progress_change):
    if not OPENAI_AVAILABLE:
        print("[DEBUG] OpenAI not available or API key/endpoint missing.")
        return None
    name = client["client_name"].split()[0]
    goal = client["goal_type"].lower()
    last_message = client["last_message_sent"]
    percent_str = f"{progress_percent:g}"
    prompt = (
        f"You are a friendly financial assistant for Dave. Generate a short, fresh, motivational, and text-friendly message for {name} about their {goal} goal. "
        f"They are at {percent_str}% of their goal. The progress this month has {progress_change}. "
        f"Do not repeat this previous message: '{last_message}'. "
        f"Use emojis, keep it under 2 sentences, and make it suitable for SMS. Add a text like from your finacial advisor Dave."
    )
    try:
        response = openai.ChatCompletion.create(
            engine=AZURE_OPENAI_DEPLOYMENT,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60,
            temperature=0.9,
        )
        msg = response.choices[0].message["content"].strip()
        print("[DEBUG] OpenAI message generated.")
        return msg
    except Exception as e:
        print(f"[DEBUG] OpenAI API call failed: {e}")
        return None

def generate_message(client, progress_percent, progress_change):
    # Try OpenAI first
    ai_msg = get_openai_message(client, progress_percent, progress_change)
    if ai_msg:
        return ai_msg
    # Fallback to templates
    name = client["client_name"].split()[0]
    goal = client["goal_type"].lower()
    last_message = client["last_message_sent"]
    percent_str = f"{progress_percent:g}"

    # Message templates
    increased_msgs = [
        f"Hi {name} 👋, awesome work! You're now at {percent_str}% of your {goal} goal. Keep that momentum going! 🎉📈",
        f"Hey {name}, your {goal} savings just grew to {percent_str}% of your goal! Fantastic progress! 🚀💪",
        f"{name}, you moved up to {percent_str}% for your {goal} goal this month! Keep crushing it! 🔥"
    ]
    same_msgs = [
        f"Hi {name} 👋, you're holding steady at {percent_str}% of your {goal} goal. Staying consistent is powerful 💪 — let's aim to level up next month! 🚀",
        f"Hey {name}, your {goal} progress is steady at {percent_str}%. Consistency counts! Let's push for more next month! ✨",
        f"{name}, you're still at {percent_str}% for your {goal} goal. Every bit counts — let's make a move next month! 💡"
    ]
    decreased_msgs = [
        f"Hi {name} 👋, your {goal} progress is at {percent_str}%. Let's refocus and get back on track next month! 💪",
        f"Hey {name}, you're at {percent_str}% for your {goal} goal. Setbacks happen — you've got this! 🚨",
        f"{name}, your {goal} goal is now at {percent_str}%. Let's rally and aim higher next month! 🌱"
    ]

    if progress_change == "increased":
        options = increased_msgs
    elif progress_change == "same":
        options = same_msgs
    else:
        options = decreased_msgs

    # Avoid repeating last message
    fresh_options = [msg for msg in options if msg != last_message]
    if not fresh_options:
        fresh_options = options  # fallback if all are repeats
    return random.choice(fresh_options) 