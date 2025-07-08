import requests
import xml.etree.ElementTree as ET

SEC_HEADERS = {"User-Agent": "OriaBot (contact@oriadawn.xyz)"}

def parse_form4_txt(url):
    try:
        # Fetch the .txt content
        response = requests.get(url.replace("-index.htm", ".txt"), headers=SEC_HEADERS, timeout=10)
        response.raise_for_status()
        text = response.text

        # Extract <XML> ... </XML> block
        xml_start = text.find("<XML>")
        xml_end = text.find("</XML>")
        if xml_start == -1 or xml_end == -1:
            print("❌ No XML found in TXT file")
            return "Unknown", 0

        xml_content = text[xml_start + 5 : xml_end]  # +5 to skip <XML>
        root = ET.fromstring(xml_content)

        # Find only nonDerivative or derivative transactions
        trade_type = "Unknown"
        amount = 0

        for node in root.findall(".//nonDerivativeTransaction") + root.findall(".//derivativeTransaction"):
            code = node.findtext(".//transactionCoding/transactionCode", "").strip()
            shares = node.findtext(".//transactionAmounts/transactionShares/value", "0").strip()

            if code in ["P", "S"]:  # Only P or S
                trade_type = "Buy" if code == "P" else "Sell"
                amount = float(shares)
                break  # Only the first valid one

        return trade_type, amount

    except Exception as e:
        print(f"❌ parse_form4_txt error: {e}")
        return "Unknown", 0