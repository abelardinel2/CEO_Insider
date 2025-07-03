import os
import requests
from datetime import datetime, timedelta

def send_summary(data):
    bot_token = os.getenv("CEO_INSIDER_BOT_TOKEN")  # New secret
    chat_id = os.getenv("CEO_INSIDER_CHAT_ID")     # New secret
    if not bot_token or not chat_id:
        print("❌ CEO Insider bot credentials missing")
        return

    message = f"📢 CEO Insider Alerts ({datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')})\n\n"
    alerts_sent = False
    for ticker, info in data["tickers"].items():
        if info["buys"] > 0 or info["sells"] > 0:
            message += f"{ticker}: Buys {info['buys']:.2f}, Sells {info['sells']:.2f}\n"
            for alert in info["alerts"]:
                message += f"  - {alert['type']} on {alert['date']}: {alert['link']}\n"
            alerts_sent = True
    if not alerts_sent:
        message += "No new insider activity detected for watchlist.\n"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    response = requests.post(url, json={"chat_id": chat_id, "text": message})
    if response.status_code != 200:
        print(f"❌ Failed to send CEO Insider message: {response.text}")
    else:
        print("✅ CEO Insider message sent successfully!")

if __name__ == "__main__":
    with open("insider_flow.json", "r") as f:
        data = json.load(f)
    send_summary(data)