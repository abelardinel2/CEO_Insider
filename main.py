import os
import json
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

                trade_type, amount = parse_form4_txt(link.replace("-index.htm", ".txt"))

                if amount == 0:
                    continue

                # Use fake price fallback if no price in XML
                amount_dollars = amount * 50.0

                if amount_dollars >= 1_000_000:
                    bias = "🚀💎🙌 Major"
                elif amount_dollars >= 500_000:
                    bias = "💰🤑 Significant"
                elif amount_dollars >= 200_000:
                    bias = "📈🤑 Notable"
                else:
                    bias = "💵 Normal"

                bias += " Accumulation" if trade_type == "Buy" else " Dump"

                send_telegram.send_alert(ticker, owner, trade_type, amount, bias, link)

    except Exception as e:
        print(f"❌ Main error: {e}")

if __name__ == "__main__":
    main()