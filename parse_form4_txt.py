import requests
from bs4 import BeautifulSoup
from lxml import etree

SEC_HEADERS = {"User-Agent": "OriaBot (contact@oriadawn.xyz)"}


def parse_form4_txt(url):
    try:
        response = requests.get(url, headers=SEC_HEADERS, timeout=10)
        response.raise_for_status()
        text = response.text

        # Try to extract embedded XML inside TXT
        if "<XML>" in text:
            xml_start = text.index("<XML>") + len("<XML>")
            xml_content = text[xml_start:]
            xml_content = xml_content.strip().split("</XML>")[0]

            root = etree.fromstring(xml_content.encode())

            code = root.findtext(".//transactionCode")
            shares = root.findtext(".//transactionShares/value")
            price = root.findtext(".//transactionPricePerShare/value")

            trade_type = "Unknown"
            if code == "P":
                trade_type = "Buy"
            elif code == "S":
                trade_type = "Sell"

            shares = float(shares) if shares else 0
            price = float(price) if price else 0

            return trade_type, shares, price

    except Exception as e:
        print(f"❌ parse_form4_txt error: {e}")

    return "Unknown", 0, 0