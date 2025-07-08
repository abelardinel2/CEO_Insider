import requests
import xml.etree.ElementTree as ET

SEC_HEADERS = {"User-Agent": "OriaBot (contact@oriadawn.xyz)"}


def parse_form4_txt(url):
    try:
        response = requests.get(url, headers=SEC_HEADERS, timeout=10)
        response.raise_for_status()
        text = response.text

        # Extract the XML part from the .txt
        xml_start = text.find("<XML>")
        xml_end = text.find("</XML>")

        if xml_start == -1 or xml_end == -1:
            print(f"❌ Could not find XML block in TXT: {url}")
            return "Unknown", 0

        xml_content = text[xml_start + len("<XML>"):xml_end]

        root = ET.fromstring(xml_content)

        code = root.findtext(".//transactionCode")
        shares = root.findtext(".//transactionShares/value")
        price = root.findtext(".//transactionPricePerShare/value")

        trade_type = "Unknown"
        if code == "P":
            trade_type = "Buy"
        elif code == "S":
            trade_type = "Sell"

        amount = 0
        if shares and price:
            try:
                amount = float(shares) * float(price)
            except:
                pass

        return trade_type, amount

    except Exception as e:
        print(f"❌ Failed to parse TXT Form 4: {e}")
        return "Unknown", 0