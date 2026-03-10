"""
Checks Telegram for /givetweet commands.
If found, exits with code 0 (success) so the workflow continues to the tweet step.
If no command found, exits with code 1 to skip tweet generation.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
chat_id = os.environ.get("TELEGRAM_CHAT_ID")

if not bot_token or not chat_id:
    print("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
    exit(1)

# Get recent messages sent to the bot
url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
response = requests.get(url, params={"limit": 20, "timeout": 0}, timeout=10)
data = response.json()

if not data.get("ok"):
    print("Failed to fetch updates from Telegram")
    exit(1)

found_command = False
command_update_id = None

for update in data.get("result", []):
    message = update.get("message", {})
    text = message.get("text", "")
    msg_chat_id = str(message.get("chat", {}).get("id", ""))

    if text.strip().lower() == "/givetweet" and msg_chat_id == str(chat_id):
        found_command = True
        command_update_id = update["update_id"]
        print(f"Found /givetweet command (update_id: {command_update_id})")

if found_command and command_update_id:
    # Acknowledge the command by advancing the offset so we don't process it again
    ack_url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    requests.get(ack_url, params={"offset": command_update_id + 1, "timeout": 0}, timeout=10)

    # Send a "generating..." message back to the user
    send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(send_url, json={
        "chat_id": chat_id,
        "text": "Got it! Generating a tweet for you now..."
    }, timeout=10)

    print("TRIGGER=true")
    exit(0)
else:
    print("No /givetweet command found.")
    print("TRIGGER=false")
    exit(1)
