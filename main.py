import json
import time
from fetch_rss import fetch_recent_form4_entries
from parse_form4_txt import parse_form4_txt
from send_alert import send_alert

WATCHLIST_FILE = "cik_watchlist.json"
VALUE_THRESHOLD = 1  # Only alert if value is over $1 (adjust as needed)

def load_watchlist():
    with open(WATCHLIST_FILE, "r") as f:
        return json.load(f)["tickers"]

def main():
    tickers = load_watchlist()
    all_alerts = []

    print("📡 Parsing SEC RSS feed...")
    entries = fetch_recent_form4_entries()

    print(f"🔎 Total entries found: {len(entries)}")

    for entry in entries:
        cik = entry.get("cik")
        ticker = next((k for k, v in tickers.items() if str(v["cik"]) == cik), None)

        if not ticker:
            continue

        try:
            trade = parse_form4_txt(entry["url"])
            if trade and trade["value"] >= VALUE_THRESHOLD:
                send_alert(
                    ticker=ticker,
                    owner=trade["owner"],
                    trade_type=trade["type"],
                    amount=trade["shares"],
                    bias=trade["bias"],
                    link=entry["url"],
                )
                all_alerts.append(entry)
                time.sleep(1)
        except Exception as e:
            print(f"❌ Error processing {entry['url']}: {e}")

    if not all_alerts:
        send_alert(message="📭 No insider alerts found in the last scan.")

if __name__ == "__main__":
    main()