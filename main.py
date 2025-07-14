from fetch_rss import fetch_insider_alerts
from send_alert import send_telegram_alert

def main():
    alerts = fetch_insider_alerts()
    if not alerts:
        send_telegram_alert("🔍 No insider alerts found today.")
        return

    for ticker, cik, link in alerts:
        message = f"📢 Insider Alert: {ticker}\n{link}"
        send_telegram_alert(message)

if __name__ == "__main__":
    main()