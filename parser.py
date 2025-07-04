# parser.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date

def parse_form4_xml(url: str) -> dict:
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception(f"Failed to fetch {url}")

    soup = BeautifulSoup(resp.text, "xml")
    period_node = soup.find("periodOfReport")
    if not period_node:
        return None

    filing_dt = datetime.strptime(period_node.text, "%Y-%m-%d").date()
    if (date.today() - filing_dt).days > 7:
        return None

    total_buys_shares = 0
    total_sells_shares = 0
    total_buys_value = 0.0
    total_sells_value = 0.0

    for txn in soup.find_all("nonDerivativeTransaction"):
        code = txn.transactionCode.string if txn.transactionCode else ""
        amount_node = txn.find("transactionShares")
        price_node = txn.find("transactionPricePerShare")
        amount = float(amount_node.value.string) if amount_node and amount_node.value else 0
        price = float(price_node.value.string) if price_node and price_node.value else 0

        if code == "P":
            total_buys_shares += amount
            total_buys_value += amount * price
        elif code == "S":
            total_sells_shares += amount
            total_sells_value += amount * price

    for txn in soup.find_all("derivativeTransaction"):
        code = txn.transactionCode.string if txn.transactionCode else ""
        amount_node = txn.find("transactionShares")
        price_node = txn.find("transactionPricePerShare")
        amount = float(amount_node.value.string) if amount_node and amount_node.value else 0
        price = float(price_node.value.string) if price_node and price_node.value else 0

        if code == "P":
            total_buys_shares += amount
            total_buys_value += amount * price
        elif code == "S":
            total_sells_shares += amount
            total_sells_value += amount * price

    return {
        "date": filing_dt,
        "buys_shares": total_buys_shares,
        "buys_value": total_buys_value,
        "sells_shares": total_sells_shares,
        "sells_value": total_sells_value
    }
