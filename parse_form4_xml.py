import requests
from bs4 import BeautifulSoup

def parse_form4_xml(url: str) -> dict:
    headers = {"User-Agent": "OriaDawnBot (contact@oriadawn.xyz)"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "xml")

    buys = 0
    sells = 0
    owner_name = soup.find("rptOwnerName").string if soup.find("rptOwnerName") else "Unknown Insider"

    for txn in soup.find_all("nonDerivativeTransaction"):
        code = txn.transactionCode.string if txn.transactionCode else ""
        acquired_or_disposed = txn.transactionAcquiredDisposedCode.string if txn.transactionAcquiredDisposedCode else ""
        amount_node = txn.find("transactionShares")
        amount = float(amount_node.value.string) if amount_node and amount_node.value else 0

        if code == "P" or acquired_or_disposed == "A":
            buys += amount
        elif code == "S" or acquired_or_disposed == "D":
            sells += amount

    return {"buys": buys, "sells": sells, "owner": owner_name}