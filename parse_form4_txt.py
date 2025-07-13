import requests
from bs4 import BeautifulSoup

def parse_form4_txt(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "lxml")

    try:
        owner = soup.find("reportingowner").find("rptownrname").text.strip()
    except:
        owner = "Unknown"

    try:
        rows = soup.find_all("nonderivativetransaction")
        latest = rows[-1] if rows else None
        if not latest:
            return None
        shares = float(latest.find("transactionshares").find("value").text)
        price = float(latest.find("transactionpricepershare").find("value").text)
        value = round(shares * price, 2)
        code = latest.find("transactioncode").text.strip()

        type_map = {
            "P": "Purchase",
            "S": "Sale",
            "A": "Award",
            "M": "Option Exercise",
            "D": "Disposition"
        }
        bias_map = {
            "P": "💰🤑 Significant Accumulation",
            "S": "⚠️ Insider Selling",
            "A": "📦 Awarded Shares",
            "M": "💼 Exercised Options",
            "D": "🔁 Disposition"
        }

        return {
            "owner": owner,
            "type": type_map.get(code, code),
            "shares": int(shares),
            "value": value,
            "bias": bias_map.get(code, "ℹ️")
        }

    except Exception as e:
        print(f"Failed to parse Form 4: {e}")
        return None
