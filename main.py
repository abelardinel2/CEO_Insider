import os
import json
import time
import feedparser
from send_alert import send_alert
from parse_form4_txt import parse_form4_txt

WATCHLIST_FILE = "cik_watchlist.json"
RSS_FEED = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=4&count=100&output=atom"
FLOW_LOG = "rss_log.json"
VALUE_THRESHOLD = int(os.getenv("VALUE_THRESHOLD", 100000))

def load_watchlist():
    with open(WATCHLIST_FILE, "r") as f:
        return {v["cik"]: k for k, v in json.load(f)["tickers"].items()}

def load_log():
    try:
        with open(FLOW_LOG, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_log(log):
    with open(FLOW_LOG, "w") as f:
        json.dump(log, f, indent=2)

def main():
    cik_map = load_watchlist()
    log = load_log()

    print("🛰️  Parsing SEC RSS feed...")
    feed = feedparser.parse(RSS_FEED)

    for entry in feed.entries:
        if "form-type" in entry and entry["form-type"] != "4":
            continue

        cik_str = entry.get("id", "").split("CIK=")[-1][:10]
        if cik_str not in cik_map:
            continue

        link = entry.get("link", "")
        if link in log:
            continue

        print(f"📄 Found Form 4 for {cik_map[cik_str]}: {link}")
        try:
            trade = parse_form4_txt(link)
            if trade and trade["value"] >= VALUE_THRESHOLD:
                send_alert(
                    ticker=cik_map[cik_str],
                    owner=trade["owner"],
                    trade_type=trade["type"],
                    amount=trade["shares"],
                    bias=trade["bias"],
                    link=link,
                )
                log[link] = {**trade, "ticker": cik_map[cik_str]}
                time.sleep(1)
        except Exception as e:
            print(f"❌ Failed to parse {link}: {e}")

    save_log(log)

if __name__ == "__main__":
    main()
