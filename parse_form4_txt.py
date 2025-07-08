import requests
import xml.etree.ElementTree as ET

SEC_HEADERS = {"User-Agent": "OriaBot (contact@oriadawn.xyz)"}

def parse_form4_txt(txt_url):
    try:
        response = requests.get(txt_url, headers=SEC_HEADERS, timeout=10)
        response.raise_for_status()
        raw = response.text

        start = raw.find("<XML>")
        end = raw.find("</XML>")
        if start == -1 or end == -1:
            print(f"❌ No XML block in {txt_url}")
            return "Unknown", 0

        xml_content = raw[start:end+6]
        root = ET.fromstring(xml_content)

        code = root.findtext(".//transactionCoding/transactionCode", default="").strip().upper()
        amount = root.findtext(".//transactionAmounts/transactionShares/value", default="0").strip()

        try:
            amount = float(amount)
        except:
            amount = 0

        if code in ["P", "S"]:
            trade_type = "Buy" if code == "P" else "Sell"
        else:
            trade_type = "Unknown"

        print(f"✅ Parsed: {code} | {amount} => {trade_type}")
        return trade_type, amount

    except Exception as e:
        print(f"❌ Parser error: {e}")
        return "Unknown", 0