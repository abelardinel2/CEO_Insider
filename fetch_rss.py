import requests
import feedparser
import json
from datetime import datetime, timedelta
from parse_form4_txt import parse_form4_txt

CIK_FILE = "cik_watchlist.json"

def load_watchlist():
    with open(CIK_FILE, "r") as f:
        return json.load(f)["tickers"]

def fetch_rss_entries():
    base_url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=4&output=atom"
    feed = feedparser.parse(base_url)
    watchlist = load_watchlist()

    recent_entries = []
    cutoff = datetime.utcnow() - timedelta(days=7)

    for entry in feed.entries:
        if "type 4" not in entry.title.lower():
            continue

        if "link" not in entry:
            continue

        cik_match = [ticker for ticker, data in watchlist.items() if str(data["cik"]) in entry.link]
        if not cik_match:
            continue

        updated = datetime.strptime(entry.updated, "%Y-%m-%dT%H:%M:%S%z")
        if updated.replace(tzinfo=None) < cutoff:
            continue

        try:
            txt_url = entry.link.replace("-index.htm", ".txt")
            raw_txt = requests.get(txt_url).text
            parsed = parse_form4_txt(raw_txt)

            if parsed:
                alert_msg = f"📢 Insider Alert: {cik_match[0]}\n👤 Insider: {parsed['owner']}\nType: {parsed['transaction_type']}\nAmount: {parsed['amount']} shares\nBias: {parsed['bias']}\nLink: {entry.link}"
                recent_entries.append(alert_msg)
        except Exception as e:
            print(f"⚠️ Error parsing entry: {e}")

    return recent_entries