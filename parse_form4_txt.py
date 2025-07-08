import requests
import xml.etree.ElementTree as ET

SEC_HEADERS = {"User-Agent": "OriaBot (contact@oriadawn.xyz)"}

def parse_form4_txt(url):
    try:
        txt_url = url.replace("-index.htm", ".txt")
        response = requests.get(txt_url, headers=SEC_HEADERS, timeout=10)
        response.raise_for_status()
        content = response.text

        # Extract <XML> ... </XML>
        start = content.find("<XML>")
        end = content.find("</XML>")
        if start == -1 or end == -1:
            print("❌ No <XML> block found in .txt")
            return "Unknown", 0

        xml_content = content[start + len("<XML>"):end].strip()
        root = ET.fromstring(xml_content)

        # Extract transaction code
        code = root.findtext(".//transactionCoding/transactionCode", default="").strip().upper()
        trade_type = "Unknown"
        if code == "P":
            trade_type = "Buy"
        elif code == "S":
            trade_type = "Sell"
        elif code == "A":
            trade_type = "Acquire"
        elif code == "D":
            trade_type = "Dispose"

        shares = root.findtext(".//transactionAmounts/transactionShares/value", default="0").strip()
        amount = float(shares)

        return trade_type, amount

    except Exception as e:
        print(f"❌ XML parse failed for TXT Form 4: {e}")
        return "Unknown", 0
