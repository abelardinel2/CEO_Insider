import os
import json
import fetcher
import send_telegram
import requests
from datetime import datetime

SEC_HEADERS = {"User-Agent": "OriaBot (contact@oriadawn.xyz)"}


def parse_form4_txt(url):
    """
    Simple parser for a .txt Form 4.
    Looks for transaction codes: P (Purchase), S (Sale).
    Returns tuple: (trade_type, amount)
    """
    try:
        response = requests.get(url, headers=SEC_HEADERS, timeout=10)
        response.raise_for_status()
        text = response.text

        lines = text.splitlines()
        amount = 0
        trade_type = "Unknown"

        for line in lines:
            line = line.strip()
            if line.startswith("Transaction Code"):
                if "P" in line:
                    trade_type = "Buy"
                elif "S" in line:
                    trade_type = "Sell"
            if "Transaction Shares" in line:
                parts = line.split()
                for part in parts:
                    try:
                        amount = float(part.replace(",", ""))
                        break
                    except ValueError:
                        continue

        return trade_type, amount

    except Exception as e:
        print(f"❌ Failed to parse TXT Form 4: {e}")
        return "Unknown", 0


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

                # Parse the .txt Form 4 to get type + shares
                trade_type, amount = parse_form4_txt(link.replace("-index.htm", ".txt"))

                # Fallback if no amount found
                if amount == 0:
                    amount = alert.get("amount_buys", 0)

                # Bias logic
                amount_dollars = amount * 100.0  # crude estimate

                if amount_dollars >= 1_000_000:
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