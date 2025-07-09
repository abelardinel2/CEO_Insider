import requests
from bs4 import BeautifulSoup

SEC_HEADERS = {"User-Agent": "OriaBot (contact@oriadawn.xyz)"}

def parse_form4_txt(url):
    try:
        response = requests.get(url, headers=SEC_HEADERS, timeout=10)
        response.raise_for_status()
        text = response.text

        # Extract the XML block inside the TXT
        xml_start = text.find("<ownershipDocument>")
        xml_end = text.find("</ownershipDocument>") + len("</ownershipDocument>")
        if xml_start == -1 or xml_end == -1:
            print("❌ No XML found in TXT")
            return "Unknown", 0

        xml = text[xml_start:xml_end]

        soup = BeautifulSoup(xml, "xml")

        # Correct buy/sell type: acquired (A) or disposed (D)
        ad_tag = soup.find("transactionAcquiredDisposedCode")
        if ad_tag and ad_tag.value:
            ad_code = ad_tag.value.text.strip()
            trade_type = "Buy" if ad_code == "A" else "Sell" if ad_code == "D" else "Unknown"
        else:
            trade_type = "Unknown"

        # Shares amount
        shares_tag = soup.find("transactionShares")
        amount = float(shares_tag.value.text.strip().replace(",", "")) if shares_tag else 0

        return trade_type, amount

    except Exception as e:
        print(f"❌ parse_form4_txt.py failed: {e}")
        return "Unknown", 0