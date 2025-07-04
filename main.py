import json
import fetcher
import send_telegram
from datetime import datetime

def main():
    try:
        # Fetch and update insider_flow.json
        fetcher.fetch_watchlist_filings()

        # Load updated insider_flow.json
        with open("insider_flow.json", "r") as f:
            data = json.load(f)

        # Loop tickers & send alerts
        for ticker, info in data["tickers"].items():
            for alert in info.get("alerts", []):
                owner = alert.get("owner", "Insider")
                trade_type = alert.get("type")
                amount = alert.get("amount_buys", 0)
                link = alert.get("link")
                bias = "🤑💰 Insider Accumulation" if trade_type == "Buy" else "💩🚽 Dumping"
                send_telegram.send_alert(ticker, owner, trade_type, amount, bias, link)

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        with open("output.log", "a") as f:
            f.write(f"{datetime.now()} - Unexpected error: {e}\n")

if __name__ == "__main__":
    main()