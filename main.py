import os
import json
import fetcher
import send_telegram
from datetime import datetime

def main():
    try:
        # Load your watchlist with tickers + CIKs
        with open("cik_watchlist.json") as f:
            tickers = json.load(f)["tickers"]

        # Fetch SEC data & update insider_flow.json
        fetcher.fetch_and_update_insider_flow(tickers)

        # Load the updated JSON
        with open("insider_flow.json") as f:
            data = json.load(f)

        # Send Telegram alerts for any new Form 4s
        for ticker, info in data["tickers"].items():
            for alert in info.get("alerts", []):
                owner = alert.get("owner", "Insider")
                trade_type = alert.get("type")
                amount = alert.get("amount_buys")
                link = alert.get("link")
                bias = "🤑💰 Insider Accumulation" if trade_type == "Buy" else "💩🚽 Insider Dump"
                send_telegram.send_alert(ticker, owner, trade_type, amount, bias, link)

    except Exception as e:
        print(f"❌ Main error: {e}")

if __name__ == "__main__":
    main()