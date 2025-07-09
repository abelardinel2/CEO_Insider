import requests

SEC_HEADERS = {"User-Agent": "OriaBot (contact@oriadawn.xyz)"}

def parse_form4_txt(url):
    owner = "Insider"
    trade_type = "Unknown"
    amount = 0.0

    try:
        resp = requests.get(url, headers=SEC_HEADERS, timeout=10)
        resp.raise_for_status()
        text = resp.text

        # Try to get owner name
        if "COMPANY CONFORMED NAME:" in text:
            owner_line = text.split("COMPANY CONFORMED NAME:")[1].split("\n")[0].strip()
            owner = owner_line

        if "<transactionCode>" in text:
            if "<transactionCode>P</transactionCode>" in text:
                trade_type = "Buy"
            elif "<transactionCode>S</transactionCode>" in text:
                trade_type = "Sell"

        if "<transactionShares>" in text:
            shares_raw = text.split("<transactionShares>")[1].split("</transactionShares>")[0]
            if "<value>" in shares_raw:
                amount = float(shares_raw.split("<value>")[1].split("</value>")[0])

    except Exception as e:
        print(f"❌ Parse TXT error: {e}")

    return owner, trade_type, amount