import requests
import xml.etree.ElementTree as ET

SEC_HEADERS = {"User-Agent": "OriaBot (contact@oriadawn.xyz)"}


def parse_form4_txt(txt_url):
    """
    Downloads a Form 4 .txt file, extracts the embedded XML,
    parses it for transactionCode, shares, and price.
    """

    try:
        response = requests.get(txt_url, headers=SEC_HEADERS, timeout=15)
        response.raise_for_status()
        content = response.text

        # Extract XML block from <XML> ... </XML>
        start = content.find("<XML>")
        end = content.find("</XML>") + len("</XML>")
        if start == -1 or end == -1:
            print(f"❌ XML block not found in TXT: {txt_url}")
            return "Unknown", 0.0, 0.0

        xml_content = content[start:end]

        # Parse XML
        root = ET.fromstring(xml_content)

        # Pick first non-derivative or derivative transaction
        node = root.find(".//nonDerivativeTransaction")
        if node is None:
            node = root.find(".//derivativeTransaction")

        if node is None:
            print(f"❌ No transaction found in XML: {txt_url}")
            return "Unknown", 0.0, 0.0

        # Transaction code: usually P (purchase) or S (sale)
        trans_code = node.findtext(".//transactionCoding/transactionCode", default="Unknown").strip().upper()

        if trans_code == "P":
            trade_type = "Buy"
        elif trans_code == "S":
            trade_type = "Sell"
        else:
            trade_type = "Unknown"

        # Number of shares
        shares = node.findtext(".//transactionAmounts/transactionShares/value", default="0").strip()
        amount = float(shares.replace(",", "")) if shares else 0.0

        # Price per share
        price = node.findtext(".//transactionAmounts/transactionPricePerShare/value", default="0").strip()
        price = float(price) if price else 0.0

        print(f"✅ Parsed: {trade_type} | Shares: {amount} | Price: {price}")

        return trade_type, amount, price

    except Exception as e:
        print(f"❌ Failed to parse Form 4 TXT: {e}")
        return "Unknown", 0.0, 0.0