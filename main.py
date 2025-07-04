import os
import json
import fetcher
import send_telegram
from datetime import datetime

def main():
    try:
        # Fetch new filings
        fetcher.fetch_and_update_insider_flow()

        # Load updated insider_flow.json
        with open("insider_flow.json", "r") as f:
            data = json.load(f)

        for ticker, info in data["tickers"].items():
            for alert in info.get("alerts", []):
                owner = alert.get("owner", "Insider")
                trade_type = alert.get("type")
                amount = alert.get("amount_buys") if trade_type == "Buy" else alert.get("amount_sells")
                link = alert.get("link")
                bias = "🤑💰 Insider Accumulation" if trade_type == "Buy" else "💩🚽 Dumping"

                send_telegram.send_alert(ticker, owner, trade_type, amount, bias, link)

    except FileNotFoundError as e:
        print(f"❌ File not found - {e}")
        with open("output.log", "a") as f:
            f.write(f"{datetime.now()} - File error: {e}\n")

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON - {e}")
        with open("output.log", "a") as f:
            f.write(f"{datetime.now()} - JSON error: {e}\n")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        with open("output.log", "a") as f:
            f.write(f"{datetime.now()} - Unexpected error: {e}\n")

if __name__ == "__main__":
    main()