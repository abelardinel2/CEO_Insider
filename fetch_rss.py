import feedparser
import json
from datetime import datetime, timedelta

def fetch_insider_alerts():
    FEED_URL = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&CIK=&type=4&company=&dateb=&owner=include&start=0&count=100&output=atom"
    feed = feedparser.parse(FEED_URL)

    # Load your CIK watchlist
    with open("cik_watchlist.json", "r") as f:
        cik_data = json.load(f)["tickers"]

    alerts = []
    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)

    for entry in feed.entries:
        title = entry.get("title", "")
        link = entry.get("link", "")
        updated_str = entry.get("updated", "")

        try:
            updated = datetime.strptime(updated_str, "%Y-%m-%dT%H:%M:%S-04:00")
        except ValueError:
            continue

        if updated < seven_days_ago:
            continue

        if not any(ftype in title for ftype in ["4", "4/A"]):
            continue

        for ticker, info in cik_data.items():
            cik = str(info["cik"])
            if cik in link:
                alerts.append((ticker, cik, link))
                break

    return alerts