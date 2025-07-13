import requests

TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

def send_alert(ticker=None, owner=None, trade_type=None, amount=None, bias=None, link=None, message=None):
    if message:
        text = message
    else:
        text = (
            f"📢 Insider Alert: {ticker}\n"
            f"👤 Insider: {owner}\n"
            f"Type: {trade_type}\n"
            f"Amount: {amount} shares\n"
            f"Bias: {bias}\n"
            f"Link: {link}"
        )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "disable_web_page_preview": True,
    }

    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"❌ Failed to send alert to Telegram: {e}")