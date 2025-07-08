import os
import json
import fetcher
import send_telegram
import requests
import re
from datetime import datetime

SEC_HEADERS = {"User-Agent": "OriaBot (contact@oriadawn.xyz)"}

def parse_form4_txt(url):
    try:
        response = requests.get(url, headers=SEC_HEADERS, timeout=10)
        response.raise_for_status()
        text = response.text

        lines = text.splitlines()

        trade_type = "Unknown"
        shares = 0
        price = 0.0

        in_table = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if "Transaction Code" in line:
                in_table = True
                continue

            if in_table:
                parts = re.split(r'\s+', line)
                if len(parts) >= 4:
                    code = parts[1].strip()
                    amt = parts[2].replace(",", "")
                    prc = parts[3]

                    if code in ["P", "S"]:
                        trade_type = "Buy" if code == "P" else "Sell"
                        shares = float(amt)
                        price = float(prc)
                        break

        dollar_value = shares * price
        return trade_type, dollar_value, shares

    except Exception as e:
        print(f"❌ TXT Parse error: {e}")
        return "Unknown", 0, 0


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

                txt_link = link.replace("-index.htm", ".txt")
                trade_type, dollar_value, shares = parse_form4_txt(txt_link)

                if trade_type == "Unknown" or shares == 0:
                    continue

                if dollar_value >= 1_000_000:
                    bias_label = "Major Accumulation" if trade_type == "Buy" else "Major Dump"
                    bias_emoji = "🚀💎🙌" if trade_type == "Buy" else "🔥💩🚽"
                elif dollar_value >= 500_000:
                    bias_label = "Significant Accumulation" if trade_type == "Buy" else "Significant Dump"
                    bias_emoji = "💰💎🤑" if trade_type == "Buy" else "💰🚽⚡️"
                elif dollar_value >= 200_000:
                    bias_label = "Notable Accumulation" if trade_type == "Buy" else "Notable Sell"
                    bias_emoji = "📈🤑" if trade_type == "Buy" else "📉🚪"
                else:
                    bias_label = "Normal Accumulation" if trade_type == "Buy" else "Normal Sell"
                    bias_emoji = "💵🧩" if trade_type == "Buy" else "💵📤"

                bias = f"{bias_emoji} {bias_label}"

                send_telegram.send_alert(ticker, owner, trade_type, shares, bias, link)

    except Exception as e:
        print(f"❌ Main error: {e}")


if __name__ == "__main__":
    main()