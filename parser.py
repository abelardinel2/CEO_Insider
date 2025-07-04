import requests
from bs4 import BeautifulSoup

def parse_form4_xml(url: str) -> dict:
    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
        raise Exception(f"Failed to fetch {url}")

    soup = BeautifulSoup(resp.text, "xml")

    total_buys_shares = 0
    total_buys_value = 0.0
    total_sells_shares = 0
    total_sells_value = 0.0

    for txn in soup.find_all("nonDerivativeTransaction"):
        code = txn.transactionCode.string if txn.transactionCode else ""
        amount = float(txn.find("transactionShares").value.string) if txn.find("transactionShares") else 0
        price_node = txn.find("transactionPricePerShare")
        price = float(price_node.value.string) if price_node and price_node.value else 0

        print(f"Non-deriv: Code={code}, Amount={amount}, Price={price}")

        if code in ["P", "M", "C", "A"]:
            total_buys_shares += amount
            total_buys_value += amount * price
        elif code == "S":
            total_sells_shares += amount
            total_sells_value += amount * price

    for txn in soup.find_all("derivativeTransaction"):
        code = txn.transactionCode.string if txn.transactionCode else ""
        amount = float(txn.find("transactionShares").value.string) if txn.find("transactionShares") else 0
        price_node = txn.find("transactionPricePerShare")
        price = float(price_node.value.string) if price_node and price_node.value else 0

        print(f"Deriv: Code={code}, Amount={amount}, Price={price}")

        if code in ["P", "M", "C", "A"]:
            total_buys_shares += amount
            total_buys_value += amount * price
        elif code == "S":
            total_sells_shares += amount
            total_sells_value += amount * price

    trade_date_node = soup.find("transactionDate")
    trade_date = trade_date_node.find("value").string if trade_date_node else "N/A"

    net_shares = total_buys_shares - total_sells_shares
    net_value = total_buys_value - total_sells_value

    print(f"✅ TOTALS → Buys: {total_buys_shares} ($ {total_buys_value:.2f}) | "
          f"Sells: {total_sells_shares} ($ {total_sells_value:.2f}) | "
          f"Net: {net_shares} ($ {net_value:.2f})")

    return {
        "buys_shares": total_buys_shares,
        "buys_value": total_buys_value,
        "sells_shares": total_sells_shares,
        "sells_value": total_sells_value,
        "net_shares": net_shares,
        "net_value": net_value,
        "date": trade_date
    }