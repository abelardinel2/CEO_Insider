import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 OriaBot (contact@oriadawn.xyz)"
}

def parse_form4_xml(index_url: str) -> dict | None:
    # Try direct XML link
    xml_url = index_url.replace("-index.htm", ".xml")
    print(f"🔍 Parsing: {xml_url}")

    xml_resp = requests.get(xml_url, headers=HEADERS)
    if xml_resp.status_code == 200:
        soup = BeautifulSoup(xml_resp.content, "xml")
    else:
        print(f"❌ Direct XML failed, fallback to index: {index_url}")
        # fallback to index page (optional)
        index_resp = requests.get(index_url, headers=HEADERS)
        if index_resp.status_code != 200:
            print(f"❌ Skipping: index page missing too: {index_url}")
            return None
        soup = BeautifulSoup(index_resp.content, "html.parser")
        return None  # index fallback parser logic could go here

    # Sample dummy parse (replace with real extraction)
    buys = sells = 0
    for txn in soup.find_all("nonDerivativeTransaction"):
        code = txn.transactionCode.string if txn.transactionCode else ""
        amount = int(txn.transactionShares.value.string)
        if code == "P":
            buys += amount
        elif code == "S":
            sells += amount

    return {
        "date": "2025-07-03",
        "buys_shares": buys,
        "sells_shares": sells,
        "buys_value": buys * 10,  # placeholder math
        "sells_value": sells * 10,
        "net_shares": buys - sells,
        "net_value": (buys - sells) * 10
    }