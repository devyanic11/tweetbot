"""
Helper script: Run this once after messaging your Telegram bot.
It will print your chat ID so you can add it as a GitHub Secret.

Usage:
    1. Create a bot via @BotFather on Telegram
    2. Send any message to your new bot
    3. Run: python notification/get_chat_id.py
    4. Copy the chat_id and add it as TELEGRAM_CHAT_ID in GitHub Secrets
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")

if not bot_token:
    print("ERROR: Set TELEGRAM_BOT_TOKEN in your .env file first.")
    exit(1)

url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
response = requests.get(url, timeout=10)
data = response.json()

if not data.get("ok") or not data.get("result"):
    print("No messages found. Make sure you've sent a message to your bot first.")
    exit(1)

for update in data["result"]:
    chat = update.get("message", {}).get("chat", {})
    if chat:
        print(f"Chat ID: {chat['id']}")
        print(f"Name: {chat.get('first_name', '')} {chat.get('last_name', '')}")
        print(f"\nAdd this to your .env or GitHub Secrets:")
        print(f"TELEGRAM_CHAT_ID={chat['id']}")
        break
