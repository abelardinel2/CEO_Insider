import requests
import feedparser
from send_alert import send_telegram_message

CIKS = {
    "NVDA": "1045810",
    "PLTR": "1739924",
    # add more if needed
}

RSS_FEED = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=4&count=100&output=atom"

def parse_rss():
    print("🛰️  Parsing SEC RSS feed...")
    feed = feedparser.parse(RSS_FEED)
    print(f"🔍 Found {len(feed.entries)} entries.")

    for entry in feed.entries:
        title = entry.get("title", "")
        link = entry.get("link", "")
        summary = entry.get("summary", "")
        cik_match = None

        for ticker, cik in CIKS.items():
            if cik in link:
                cik_match = cik
                break

        if cik_match:
            print(f"✅ Match found: {title}")
            if "Form 4" in title:
                msg = (
                    f"📢 Insider Alert: {ticker}\n"
                    f"<b>{title}</b>\n"
                    f"<a href=\"{link}\">View Filing</a>"
                )
                send_telegram_message(msg)
        else:
            print(f"⏭️ No match for: {title}")

if __name__ == "__main__":
    parse_rss()