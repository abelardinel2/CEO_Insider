# send_alert.py (combined version)

import os
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"❌ Telegram send error: {response.status_code} - {response.text}")
        else:
            print("✅ Telegram message sent.")
    except Exception as e:
        print(f"❌ Exception while sending Telegram message: {e}")

def send_alert(ticker, owner, trade_type, amount, bias, link):
    message = (
        f"<b>📢 Insider Alert: {ticker}</b>\n"
        f"👤 Insider: {owner}\n"
        f"Type: {trade_type}\n"
        f"Amount: {amount:,.0f} shares\n"
        f"Bias: {bias}\n"
        f"🔗 <a href='{link}'>View Filing</a>"
    )
    send_telegram_message(message)