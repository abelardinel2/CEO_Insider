import os
import requests

def send_alert(ticker, owner, trade_type, shares, bias, link):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    message = (
        f"📢 Insider Alert: {ticker}\n"
        f"👤 Insider: {owner}\n"
        f"Type: {trade_type}\n"
        f"Amount: {shares:,.0f} shares\n"
        f"Bias: {bias}\n"
        f"Link: {link}"
    )

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    response = requests.post(url, data={"chat_id": chat_id, "text": message})

    if response.status_code == 200:
        print(f"✅ Alert sent for {ticker}")
    else:
        print(f"❌ Telegram send failed: {response.text}")