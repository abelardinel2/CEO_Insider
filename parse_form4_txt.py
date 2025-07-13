import requests
from bs4 import BeautifulSoup

def parse_form4_txt(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.content, "xml")

    code_tag = soup.find("transactionCode")
    shares_tag = soup.find("transactionShares")
    price_tag = soup.find("transactionPricePerShare")
    owner_tag = soup.find("reportingOwnerId")

    if not (code_tag and shares_tag and price_tag and owner_tag):
        return None

    code = code_tag.text.strip()
    shares = float(shares_tag.value.text)
    price = float(price_tag.value.text)
    owner = owner_tag.rptOwnerName.text.strip()
    value = shares * price

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