import os
import requests

def send_alert(ticker, owner, trade_type, amount, bias, link):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        print("Missing Telegram credentials.")
        return

    msg = f"\U0001F4E2 Insider Alert: {ticker}\n" +           f"\U0001F464 Insider: {owner}\n" +           f"Type: {trade_type}\n" +           f"Amount: {amount} shares\n" +           f"Bias: {bias}\n" +           f"Link: {link}"

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": msg, "disable_web_page_preview": True}

    try:
        r = requests.post(url, json=payload)
        if r.status_code != 200:
            print(f"Failed to send alert for {ticker}")
    except Exception as e:
        print(f"Telegram error: {e}")
