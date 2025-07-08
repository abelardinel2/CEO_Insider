import os
import json
import fetcher
from parse_form4_txt import parse_form4_txt
import send_telegram

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
                txt_link = link.replace("-index.htm", ".txt")

                trade_type, amount = parse_form4_txt(txt_link)
                print(f"🔗 Checked {txt_link} => {trade_type} {amount}")

                if trade_type == "Unknown" or amount == 0:
                    continue

                dollars = amount * 100.0
                if dollars >= 1_000_000:
                    bias = "🚀💎🙌 Major Accumulation" if trade_type == "Buy" else "🔥💩 Major Dump"
                elif dollars >= 500_000:
                    bias = "💰🤑 Significant Accumulation" if trade_type == "Buy" else "💰⚡️ Significant Dump"
                elif dollars >= 200_000:
                    bias = "📈🤑 Notable Accumulation" if trade_type == "Buy" else "📉🚪 Notable Sell"
                else:
                    bias = "💵🧩 Normal Accumulation" if trade_type == "Buy" else "💵📤 Normal Sell"

                send_telegram.send_alert(ticker, alert["owner"], trade_type, amount, bias, link)

    except Exception as e:
        print(f"❌ Main error: {e}")

if __name__ == "__main__":
    main()