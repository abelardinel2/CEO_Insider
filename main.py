import os
import json
import requests
from datetime import datetime

import fetcher
import send_telegram
from parse_form4_txt import parse_form4_txt

def main():
    try:
        with open("cik_watchlist.json") as f:
            tickers = json.load(f)

        fetcher.fetch_and_update_insider_flow(tickers)

        with open("insider_flow.json") as f:
            data = json.load(f)

        for ticker, info in data["tickers"].items():
            for alert in info.get("alerts", []):
                link = alert.get("link")
                owner = alert.get("owner", "Insider")

                trade_type, amount = parse_form4_txt(link)

                if trade_type == "Unknown" or amount <= 0:
                    continue  # Skip non-P/S

                dollar_value = amount * 100.0  # Assumption

                if dollar_value >= 1_000_000:
                    bias = "🚀💎🙌 Major Accumulation" if trade_type == "Buy" else "🔥💩🚽 Major Dump"
                elif dollar_value >= 500_000:
                    bias = "💰💎🤑 Significant Accumulation" if trade_type == "Buy" else "💰🚽⚡️ Significant Dump"
                elif dollar_value >= 200_000:
                    bias = "📈🤑 Notable Buy" if trade_type == "Buy" else "📉🚪 Notable Sell"
                else:
                    bias = "💵🧩 Normal Buy" if trade_type == "Buy" else "💵📤 Normal Sell"

                send_telegram.send_alert(ticker, owner, trade_type, amount, bias, link)

    except Exception as e:
        print(f"❌ Main error: {e}")

if __name__ == "__main__":
    main()