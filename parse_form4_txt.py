import requests
from bs4 import BeautifulSoup

def parse_form4_txt(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None

        soup = BeautifulSoup(r.content, "xml")
        transaction = soup.find("nonDerivativeTransaction")
        if not transaction:
            return None

        code = transaction.find("transactionCode").text.strip()
        shares = float(transaction.find("transactionShares").find("value").text.strip())
        price_tag = transaction.find("transactionPricePerShare")
        price = float(price_tag.find("value").text.strip()) if price_tag else 0.0
        value = shares * price
        owner = soup.find("reportingOwnerId").find("rptOwnerName").text.strip()

        trade_type = "Buy" if code in ["P", "A", "M"] else "Sell"
        bias = "💰🤑 Accumulation" if trade_type == "Buy" else "📉 Distribution"

        return {
            "owner": owner,
            "type": trade_type,
            "code": code,
            "shares": shares,
            "price": price,
            "value": value,
            "bias": bias,
            "url": url
        }
    except Exception as e:
        print(f"❌ Failed to parse form: {e}")
        return None
