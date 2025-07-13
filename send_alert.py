import os
import requests
import logging

# Configure logging
logging.basicConfig(
    filename="edgar_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def send_alert(ticker, owner, trade_type, amount, bias, link):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        logging.error(f"Missing Telegram credentials: BOT_TOKEN={bot_token}, CHAT_ID={chat_id}")
        print(f"❌ Missing Telegram credentials: BOT_TOKEN={bot_token}, CHAT_ID={chat_id}")
        return

    message = (
        f"📢 Insider Alert: {ticker}\n"
        f"👤 Insider: {owner}\n"
        f"Type: {trade_type}\n"
        f"Amount: {amount:,.0f} shares\n"
        f"Bias: {bias}\n"
        f"Link: {link}"
    )

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        response = requests.post(url, data={"chat_id": chat_id, "text": message}, timeout=10)
        response.raise_for_status()
        logging.info(f"Alert sent for {ticker}")
        print(f"✅ Alert sent for {ticker}")
    except Exception as e:
        logging.error(f"Telegram send failed for {ticker}: {str(e)}, Response: {response.text if 'response' in locals() else 'No response'}")
        print(f"❌ Telegram send failed for {ticker}: {e}")