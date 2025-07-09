import os
import json
import fetcher
from parse_form4_txt import parse_form4_txt
import send_telegram
from datetime import datetime

def main():
    try:
        with open("cik_watchlist.json") as f:
            tickers = json.load(f)

        fetcher.fetch_and_update_insider_flow(tickers)

        with open("insider_flow.json") as f:
            data = json.load(f)

        for ticker, info in data["tickers"].items():
            for alert in info.get("alerts", []):
                link = alert["link"]

                trade_type, shares, price, owner = parse_form4_txt(link)

                if shares == 0 or price == 0 or trade_type == "Unknown":
                    continue

                amount_dollars = shares * price

                if amount_dollars >= 1_000_000:
                    bias = "🚀💎🙌 Major Accumulation" if trade_type == "Buy" else "🔥💩🚽 Major Dump"
                elif amount_dollars >= 500_000:
                    bias = "💰🤑 Significant Accumulation" if trade_type == "Buy" else "💰🚽 Significant Dump"
                elif amount_dollars >= 200_000:
                    bias = "📈🤑 Notable Accumulation" if trade_type == "Buy" else "📉🚪 Notable Sell"
                else:
                    bias = "💵 Normal Accumulation" if trade_type == "Buy" else "💵 Normal Sell"

                print(f"✅ {ticker}: {trade_type} {shares} @ ${price} → ${amount_dollars:,.0f}")

                send_telegram.send_alert(ticker, owner, trade_type, shares, bias, link)

    except Exception as e:
        print(f"❌ Main error: {e}")

if __name__ == "__main__":
    main()