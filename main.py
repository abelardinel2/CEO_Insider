import json
import feedparser
from send_alert import send_telegram_message

WATCHLIST_FILE = "cik_watchlist.json"
RSS_FEED = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=4&count=100&output=atom"

def load_ciks():
    with open(WATCHLIST_FILE, "r") as f:
        return {v["cik"]: k for k, v in json.load(f)["tickers"].items()}

def parse_rss_and_alert():
    print("🛰️ Parsing SEC RSS feed...")
    feed = feedparser.parse(RSS_FEED)
    print(f"🔍 Total entries found: {len(feed.entries)}")

    cik_map = load_ciks()

    for entry in feed.entries:
        title = entry.get("title", "")
        link = entry.get("link", "")
        summary = entry.get("summary", "")
        
        # Skip non-Form 4 filings
        if "Form 4" not in title:
            continue

        # Extract CIK from link (EDGAR format includes it)
        for cik in cik_map:
            if cik in link:
                ticker = cik_map[cik]
                print(f"✅ Match: {ticker} ({cik}) | {title}")
                msg = (
                    f"📢 Insider Alert: {ticker}\n"
                    f"👤 {title}\n"
                    f"<a href=\"{link}\">🔗 View Filing</a>"
                )
                send_telegram_message(msg)
                break

if __name__ == "__main__":
    parse_rss_and_alert()