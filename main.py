import json
import time
from fetcher import fetch_recent_form4_urls
from parse_form4_txt import parse_form4_txt
from send_alert import send_alert

WATCHLIST_FILE = "cik_watchlist.json"
VALUE_THRESHOLD = 1  # Minimum value for alert

def load_watchlist():
    with open(WATCHLIST_FILE, "r") as f:
        return json.load(f)["tickers"]

def main():
    tickers = load_watchlist()

    for ticker, info in tickers.items():
        cik = info["cik"]
        print(f"📡 Scanning: {ticker} (CIK {cik})")
        form_urls = fetch_recent_form4_urls(cik)

        for url in form_urls:
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
                    time.sleep(1)
            except Exception as e:
                print(f"❌ Failed to process {url}: {e}")

if __name__ == "__main__":
    main()
