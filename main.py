import os
import json
import fetcher
import send_telegram
from datetime import datetime

def main():
    try:
        with open("cik_watchlist.json") as f:
            tickers = json.load(f)["tickers"]

        fetcher.fetch_and_update_insider_flow(tickers)

        with open("insider_flow.json") as f:
            data = json.load(f)

        # ✅ Only send unsent alerts
        for ticker, info in data["tickers"].items():
            alerts = info.get("alerts", [])
            if alerts:
                for alert in alerts:
                    owner = alert.get("owner", "Insider")
                    trade_type = alert.get("type")
                    amount = alert.get("amount_buys")
                    link = alert.get("link")
                    bias = "🤑💰 Insider Accumulation" if trade_type == "Buy" else "💩🚽 Insider Dump"
                    send_telegram.send_alert(ticker, owner, trade_type, amount, bias, link)
                # ✅ After sending, clear alerts so we don’t resend next run
                info["alerts"] = []

        # ✅ Save cleared alerts back
        with open("insider_flow.json", "w") as f:
            json.dump(data, f, indent=2)

    except Exception as e:
        print(f"❌ Main error: {e}")

if __name__ == "__main__":
    main()