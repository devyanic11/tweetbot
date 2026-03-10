import os
import requests
from dotenv import load_dotenv

def send_telegram_message(tweet_text, source_url=None):
    """
    Sends a tweet to the configured Telegram chat via Bot API.
    Completely free, no rate limits for normal usage.
    """
    load_dotenv()
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("WARNING: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set. Skipping Telegram send.")
        return False

    # Build the message
    if source_url:
        message = f"{tweet_text}\n\nSource: {source_url}"
    else:
        message = tweet_text

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        if result.get("ok"):
            print("Tweet sent to Telegram successfully!")
            return True
        else:
            print(f"Telegram API error: {result}")
            return False
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return False
