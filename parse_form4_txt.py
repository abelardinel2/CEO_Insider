import requests
import re

def parse_form4_txt(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to fetch form at {url}")
            return None, 0, 0

        content = response.text

        # Detect acquisition or disposition (A or D)
        ad_match = re.search(r"<value>([AD])</value>", content)
        ad_flag = ad_match.group(1) if ad_match else None

        if ad_flag == "A":
            trade_type = "Buy"
        elif ad_flag == "D":
            trade_type = "Sell"
        else:
            trade_type = None

        # Extract number of shares acquired or disposed
        amount_match = re.search(r"<transactionShares>\s*<value>([\d.,]+)</value>", content)
        amount = float(amount_match.group(1).replace(",", "")) if amount_match else 0

        # Extract price per share
        price_match = re.search(r"<transactionPricePerShare>\s*<value>([\d.]+)</value>", content)
        price = float(price_match.group(1)) if price_match else 0.0

        # Fallback if price is zero
        if not price or price == 0.0:
            price = 1.00

        return trade_type, amount, price

    except Exception as e:
        print(f"❌ Error parsing form at {url}: {e}")
        return None, 0, 0