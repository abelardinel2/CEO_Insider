import os
import requests

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_alert(ticker, owner, trade_type, amount, bias, link):
    message = (
        f"📢 Insider Alert: {ticker}\n"
        f"👤 Insider: {owner}\n"
        f"Type: {trade_type}\n"
        f"Amount: {amount:,} shares\n"
        f"Bias: {bias}\n"
        f"Link: {link}"
    )
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": True
    }
    response = requests.post(url, data=data)
    if not response.ok:
        print(f"❌ Telegram error: {response.text}")
