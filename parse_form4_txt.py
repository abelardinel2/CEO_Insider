import requests
from lxml import etree

SEC_HEADERS = {"User-Agent": "OriaBot (contact@oriadawn.xyz)"}


def parse_form4_txt(url):
    try:
        response = requests.get(url, headers=SEC_HEADERS, timeout=10)
        response.raise_for_status()
        text = response.text

        # -------- Try embedded XML first -------
        if "<XML>" in text:
            xml_start = text.index("<XML>") + len("<XML>")
            xml_content = text[xml_start:].split("</XML>")[0]

            root = etree.fromstring(xml_content.encode())

            code = root.findtext(".//transactionCode")
            shares = root.findtext(".//transactionShares/value")
            price = root.findtext(".//transactionPricePerShare/value")

            if code:
                trade_type = "Buy" if code == "P" else "Sell" if code == "S" else "Unknown"
                shares = float(shares) if shares else 0
                price = float(price) if price else 0

                if trade_type != "Unknown" and shares > 0 and price > 0:
                    return trade_type, shares, price

        # -------- If XML fails, fallback to text lines -------
        lines = text.splitlines()
        trade_type = "Unknown"
        shares = 0
        price = 0

        for line in lines:
            if "Transaction Code" in line:
                if "P" in line:
                    trade_type = "Buy"
                elif "S" in line:
                    trade_type = "Sell"
            if "Transaction Shares" in line:
                parts = line.split()
                for part in parts:
                    try:
                        shares = float(part.replace(",", ""))
                        break
                    except ValueError:
                        continue
            if "Transaction Price Per Share" in line:
                parts = line.split()
                for part in parts:
                    try:
                        price = float(part.replace(",", ""))
                        break
                    except ValueError:
                        continue

        return trade_type, shares, price

    except Exception as e:
        print(f"❌ parse_form4_txt fallback error: {e}")

    return "Unknown", 0, 0