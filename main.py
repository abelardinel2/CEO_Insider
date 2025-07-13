from fetch_rss import fetch_rss_entries
from send_alert import send_telegram_message

def main():
    print("🛰️ Parsing SEC RSS feed...")
    entries = fetch_rss_entries()

    if not entries:
        print("🔍 Total entries found: 0")
        send_telegram_message("📭 No insider alerts found.")
        return

    for alert in entries:
        send_telegram_message(alert)

if __name__ == "__main__":
    main()