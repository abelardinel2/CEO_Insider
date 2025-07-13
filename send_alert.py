import os
import requests

def send_alert(ticker, owner, trade_type, amount, bias, link):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    message = (
        f"📢 Insider Alert: {ticker}
"
        f"👤 Insider: {owner}
"
        f"Type: {trade_type}
"
        f"Amount: {amount:,.0f} shares
"
        f"Bias: {bias}
"
        f"Link: {link}"
    )

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    response = requests.post(url, data={"chat_id": chat_id, "text": message})

    if response.status_code == 200:
        print(f"✅ Alert sent for {ticker}")
    else:
        print(f"❌ Telegram send failed: {response.text}")