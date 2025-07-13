import requests
from bs4 import BeautifulSoup

def parse_form4_txt(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.content, "xml")
    code = soup.find("transactionCode").text
    shares = float(soup.find("transactionShares").value.text)
    price = float(soup.find("transactionPricePerShare").value.text)
    value = shares * price
    owner = soup.find("reportingOwnerId").rptOwnerName.text

    bias = "💰🤑 Significant Accumulation" if code == "A" else "📉 Likely Distribution"
    trade_type = "Buy" if code == "A" else "Sell"

    return {
        "owner": owner,
        "type": trade_type,
        "shares": shares,
        "price": price,
        "value": value,
        "bias": bias,
    }
