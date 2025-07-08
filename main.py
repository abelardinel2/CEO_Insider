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
        dollar_value = 0.0

        for line in lines:
            line = line.strip()

            # Debug: print matching lines
            if "Transaction Code" in line or "Transaction Shares" in line or "Transaction Price Per Share" in line:
                print(f"✅ LINE: {line}")

            if re.search(r"Transaction\s+Code", line):
                if "P" in line:
                    trade_type = "Buy"
                elif "S" in line:
                    trade_type = "Sell"

            if re.search(r"Transaction\s+Shares", line):
                match = re.search(r"(\d[\d,]*)", line)
                if match:
                    shares = float(match.group(1).replace(",", ""))

            if re.search(r"Transaction Price Per Share", line):
                match = re.search(r"(\d+(\.\d+)?)", line)
                if match:
                    price = float(match.group(1))
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

                txt_url = link.replace("-index.htm", ".txt")
                trade_type, dollar_value, shares = parse_form4_txt(txt_url)

                if trade_type == "Unknown":
                    print(f"⚠️ SKIP {ticker}: No P/S found")
                    continue

                amount = dollar_value if dollar_value > 0 else shares * 10  # fallback est.

                if amount >= 1_000_000:
                    label = "Major Accumulation" if trade_type == "Buy" else "Major Dump"
                    emoji = "🚀💎🙌" if trade_type == "Buy" else "🔥💩🚽"
                elif amount >= 500_000:
                    label = "Significant Accumulation" if trade_type == "Buy" else "Significant Dump"
                    emoji = "💰💎🤑" if trade_type == "Buy" else "💰🚽⚡️"
                elif amount >= 200_000:
                    label = "Notable Accumulation" if trade_type == "Buy" else "Notable Sell"
                    emoji = "📈🤑" if trade_type == "Buy" else "📉🚪"
                else:
                    label = "Normal Accumulation" if trade_type == "Buy" else "Normal Sell"
                    emoji = "💵🧩" if trade_type == "Buy" else "💵📤"

                bias = f"{emoji} {label}"

                send_telegram.send_alert(ticker, owner, trade_type, amount, bias, link)

    except Exception as e:
        print(f"❌ Main error: {e}")


if __name__ == "__main__":
    main()