import os
import requests

def send_alert(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        r = requests.post(url, data=data)
        r.raise_for_status()
    except Exception as e:
        print(f"Error sending alert: {e}")