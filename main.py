import json
import time
from fetcher import fetch_recent_form4_urls
from parse_form4_txt import parse_form4_txt
from send_alert import send_alert

WATCHLIST_FILE = "watchlist.json"
FLOW_FILE = "insider_flow.json"
VALUE_THRESHOLD = 1  # Set to $1 for testing

def load_watchlist():
    with open(WATCHLIST_FILE, "r") as f:
        return json.load(f)["tickers"]

def load_flow_log():
    try:
        with open(FLOW_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_flow_log(log):
    with open(FLOW_FILE, "w") as f:
        json.dump(log, f, indent=2)

def main():
    tickers = load_watchlist()
    flow_log = load_flow_log()

    for ticker, info in tickers.items():
        cik = info["cik"]
        print(f"📡 Scanning: {ticker} (CIK {cik})")
        form_urls = fetch_recent_form4_urls(cik)

        for url in form_urls:
            if url in flow_log:
                continue  # Skip already processed
            try:
                trade = parse_form4_txt(url)
                if trade and trade["value"] >= VALUE_THRESHOLD:
                    send_alert(
                        ticker=ticker,
                        owner=trade["owner"],
                        trade_type=trade["type"],
                        amount=trade["shares"],
                        bias=trade["bias"],
                        link=url,
                    )
                    flow_log[url] = {
                        "ticker": ticker,
                        "owner": trade["owner"],
                        "type": trade["type"],
                        "shares": trade["shares"],
                        "value": trade["value"],
                    }
                    time.sleep(1)
            except Exception as e:
                print(f"❌ Failed to process {url}: {e}")

    save_flow_log(flow_log)

if __name__ == "__main__":
    main()