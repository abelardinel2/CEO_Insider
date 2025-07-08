import requests
import xml.etree.ElementTree as ET

SEC_HEADERS = {"User-Agent": "OriaBot (contact@oriadawn.xyz)"}

def parse_form4_txt(txt_url):
    try:
        # Download the .txt file
        response = requests.get(txt_url, headers=SEC_HEADERS, timeout=10)
        response.raise_for_status()
        raw = response.text

        # Extract the <XML> block only
        start = raw.find("<XML>")
        end = raw.find("</XML>")
        if start == -1 or end == -1:
            print("❌ No <XML> block found in TXT")
            return "Unknown", 0

        xml_content = raw[start:end+6]

        # Parse XML block
        root = ET.fromstring(xml_content)

        # Extract transaction code & amount
        code = root.findtext(".//transactionCoding/transactionCode", default="").strip().upper()
        amount = root.findtext(".//transactionAmounts/transactionShares/value", default="0").strip()

        if not code:
            code = root.findtext(".//transactionAcquiredDisposedCode/value", default="").strip().upper()

        try:
            amount = float(amount)
        except:
            amount = 0

        # Only return if it’s a real P or S
        if code not in ["P", "S"]:
            return "Unknown", 0

        trade_type = "Buy" if code == "P" else "Sell"
        return trade_type, amount

    except Exception as e:
        print(f"❌ parse_form4_txt failed: {e}")
        return "Unknown", 0