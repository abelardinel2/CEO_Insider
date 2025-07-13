import os
import requests

def send_alert(ticker, owner, trade_type, amount, bias, link):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    msg = (
        f"📢 Insider Alert: {ticker}\n"
        f"👤 Insider: {owner}\n"
        f"Type: {trade_type}\n"
        f"Amount: {amount:,.0f} shares\n"
        f"Bias: {bias}\n"
        f"Link: {link}"
    )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    res = requests.post(url, data={"chat_id": chat_id, "text": msg})

    if res.status_code == 200:
        print(f"✅ Alert sent for {ticker}")
    else:
        print(f"❌ Telegram failed: {res.text}")
