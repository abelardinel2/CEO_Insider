import requests
import xml.etree.ElementTree as ET

SEC_HEADERS = {"User-Agent": "OriaBot (contact@oriadawn.xyz)"}


def parse_form4_txt(txt_url):
    try:
        response = requests.get(txt_url, headers=SEC_HEADERS, timeout=15)
        response.raise_for_status()
        content = response.text

        start = content.find("<XML>")
        end = content.find("</XML>") + len("</XML>")
        if start == -1 or end == -1:
            print(f"❌ XML block not found: {txt_url}")
            return "Unknown", 0.0, 0.0

        xml_content = content[start:end]

        root = ET.fromstring(xml_content)

        node = root.find(".//nonDerivativeTransaction")
        if node is None:
            node = root.find(".//derivativeTransaction")

        if node is None:
            print(f"❌ No transaction found: {txt_url}")
            return "Unknown", 0.0, 0.0

        code = node.findtext(".//transactionCoding/transactionCode", default="").upper()
        if code == "P":
            trade_type = "Buy"
        elif code == "S":
            trade_type = "Sell"
        else:
            trade_type = "Unknown"

        shares = node.findtext(".//transactionAmounts/transactionShares/value", default="0")
        price = node.findtext(".//transactionAmounts/transactionPricePerShare/value", default="0")

        shares = float(shares)
        price = float(price)

        return trade_type, shares, price

    except Exception as e:
        print(f"❌ TXT parse error: {e}")
        return "Unknown", 0.0, 0.0