import os
import json
import fetcher
import send_telegram
import requests
from datetime import datetime
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

                trade_type, amount, price = parse_form4_txt(link.replace("-index.htm", ".txt"))

                if not trade_type or amount == 0:
                    continue  # skip incomplete or non-trade forms

                amount_dollars = amount * price

                # Label tiers
                if amount_dollars >= 1:
                    bias_label = "Major Accumulation" if trade_type == "Buy" else "Major Dump"
                    bias_emoji = "🚀💎🙌" if trade_type == "Buy" else "🔥💩🚽"
                elif amount_dollars >= 500_000:
                    bias_label = "Significant Accumulation" if trade_type == "Buy" else "Significant Dump"
                    bias_emoji = "💰💎🤑" if trade_type == "Buy" else "💰🚽⚡️"
                elif amount_dollars >= 200_000:
                    bias_label = "Notable Accumulation" if trade_type == "Buy" else "Notable Sell"
                    bias_emoji = "📈🤑" if trade_type == "Buy" else "📉🚪"
                else:
                    bias_label = "Normal Accumulation" if trade_type == "Buy" else "Normal Sell"
                    bias_emoji = "💵🧩" if trade_type == "Buy" else "💵📤"

                bias = f"{bias_emoji} {bias_label}"

                send_telegram.send_alert(ticker, owner, trade_type, amount, bias, link)

    except Exception as e:
        print(f"❌ Main error: {e}")

if __name__ == "__main__":
    main()