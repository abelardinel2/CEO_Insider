import requests
import xml.etree.ElementTree as ET

SEC_HEADERS = {"User-Agent": "OriaBot (contact@oriadawn.xyz)"}

def parse_form4_txt(txt_url):
    try:
        response = requests.get(txt_url, headers=SEC_HEADERS, timeout=10)
        response.raise_for_status()
        text = response.text

        # Extract embedded XML part
        start = text.find("<ownershipDocument>")
        end = text.find("</ownershipDocument>") + len("</ownershipDocument>")
        xml_part = text[start:end]

        root = ET.fromstring(xml_part)

        code = root.findtext(".//transactionCode", default="N/A")
        shares = float(root.findtext(".//transactionShares/value", default="0"))
        price = float(root.findtext(".//transactionPricePerShare/value", default="0"))
        owner = root.findtext(".//reportingOwnerId/rptOwnerName", default="Unknown")

        if "P" in code:
            trade_type = "Buy"
        elif "S" in code:
            trade_type = "Sell"
        else:
            trade_type = "Unknown"

        return trade_type, shares, price, owner

    except Exception as e:
        print(f"❌ Parse error: {e}")
        return "Unknown", 0, 0, "Unknown"