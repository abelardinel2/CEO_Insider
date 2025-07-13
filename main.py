import json
import time
import os
from dotenv import load_dotenv
import logging

load_dotenv()

from fetcher import fetch_recent_form4_urls
from parse_form4_txt import parse_form4_txt
from send_alert import send_alert

WATCHLIST_FILE = "cik_watchlist.json"
FLOW_FILE = "insider_flow.json"
VALUE_THRESHOLD = 1  # Set to $1 for testing

# Configure logging
logging.basicConfig(
    filename="edgar_errors.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def load_watchlist():
    try:
        with open(WATCHLIST_FILE, "r") as f:
            return json.load(f)["tickers"]
    except FileNotFoundError:
        logging.error(f"{WATCHLIST_FILE} not found")
        print(f"❌ {WATCHLIST_FILE} not found")
        return {}

def load_flow_log():
    try:
        with open(FLOW_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_flow_log(log):
    with open(FLOW_FILE, "w") as f:
        json.dump(log, f, indent=2)

def update_watchlist(ticker, trade_type):
    with open(WATCHLIST_FILE, "r") as f:
        watchlist = json.load(f)
    if trade_type == "Buy":
        watchlist["tickers"][ticker]["buys"] += 1
    elif trade_type == "Sell":
        watchlist["tickers"][ticker]["sells"] += 1
    watchlist["tickers"][ticker]["alerts"].append({
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "trade_type": trade_type
    })
    with open(WATCHLIST_FILE, "w") as f:
        json.dump(watchlist, f, indent=2)

def main():
    tickers = load_watchlist()
    if not tickers:
        print("❌ No tickers in watchlist")
        return

    flow_log = load_flow_log()

    for ticker, info in tickers.items():
        cik = str(info["cik"]).zfill(10)  # Pad CIK
        print(f"📡 Scanning: {ticker} (CIK {cik})")
        form_urls = fetch_recent_form4_urls(cik)

        if not form_urls:
            logging.info(f"No Form 4 URLs for {ticker}")
            print(f"❌ No Form 4 URLs for {ticker}")
            continue

        for url in form_urls:
            if url in flow_log:
                logging.info(f"Skipping processed URL: {url}")
                print(f"ℹ️ Skipping processed URL: {url}")
                continue
            try:
                trades = parse_form4_txt(url)
                if not trades:
                    logging.info(f"No valid trades in {url}")
                    print(f"ℹ️ No valid trades in {url}")
                    continue

                for trade in trades:
                    if trade["value"] >= VALUE_THRESHOLD:
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
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                        }
                        update_watchlist(ticker, trade["type"])
                        save_flow_log(flow_log)
                        time.sleep(1)
            except Exception as e:
                logging.error(f"Failed to process {url}: {str(e)}")
                print(f"❌ Failed to process {url}: {e}")

if __name__ == "__main__":
    main()