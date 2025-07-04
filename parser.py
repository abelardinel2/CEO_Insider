import requests
from bs4 import BeautifulSoup
from datetime import datetime, date

def parse_form4_xml(url: str) -> dict:
    """
    ✅ Handles:
    - Direct XML (with fallback)
    - Index HTML page
    """
    print(f"🔍 Parsing: {url}")

    def fetch_and_parse_xml(xml_url):
        xml_resp = requests.get(xml_url, timeout=10)
        if xml_resp.status_code != 200:
            return None
        return BeautifulSoup(xml_resp.text, "xml")

    xml_soup = None

    if url.endswith(".xml"):
        xml_soup = fetch_and_parse_xml(url)

        if xml_soup is None or not xml_soup.find("periodOfReport"):
            print(f"❌ Direct XML failed, fallback to index: {url}")
            # fallback: treat as index
            url = url.replace(".xml", "-index.htm")

    if not xml_soup:
        # treat as index page
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            raise Exception(f"Failed to fetch index page {url}")

        soup = BeautifulSoup(resp.text, "html.parser")
        xml_link = None
        for link in soup.find_all("a"):
            href = link.get("href", "")
            if href.endswith(".xml"):
                xml_link = href
                break

        if not xml_link:
            raise Exception(f"No .xml link found in index page {url}")

        base = "/".join(url.split("/")[:-1])
        xml_url = f"{base}/{xml_link}"
        print(f"✅ Found XML: {xml_url}")

        xml_soup = fetch_and_parse_xml(xml_url)
        if xml_soup is None:
            raise Exception(f"Failed to fetch fallback XML {xml_url}")

    # ✅ Now parse
    period_node = xml_soup.find("periodOfReport")
    if not period_node:
        return None

    filing_dt = datetime.strptime(period_node.text, "%Y-%m-%d").date()
    if (date.today() - filing_dt).days > 7:
        return None

    total_buys_shares = 0
    total_buys_value = 0.0
    total_sells_shares = 0
    total_sells_value = 0.0

    for txn in xml_soup.find_all("nonDerivativeTransaction"):
        code = txn.transactionCode.string if txn.transactionCode else ""
        amount_node = txn.find("transactionShares")
        price_node = txn.find("transactionPricePerShare")
        amount = float(amount_node.value.string) if amount_node and amount_node.value else 0
        price = float(price_node.value.string) if price_node and price_node.value else 0

        if code in ["P", "M", "C", "A"]:
            total_buys_shares += amount
            total_buys_value += amount * price
        elif code == "S":
            total_sells_shares += amount
            total_sells_value += amount * price

    for txn in xml_soup.find_all("derivativeTransaction"):
        code = txn.transactionCode.string if txn.transactionCode else ""
        amount_node = txn.find("transactionShares")
        price_node = txn.find("transactionPricePerShare")
        amount = float(amount_node.value.string) if amount_node and amount_node.value else 0
        price = float(price_node.value.string) if price_node and price_node.value else 0

        if code in ["P", "M", "C", "A"]:
            total_buys_shares += amount
            total_buys_value += amount * price
        elif code == "S":
            total_sells_shares += amount
            total_sells_value += amount * price

    net_shares = total_buys_shares - total_sells_shares
    net_value = total_buys_value - total_sells_value

    print(f"✅ Buys: {total_buys_shares} | Sells: {total_sells_shares} | Net: {net_shares}")
    return {
        "date": filing_dt.isoformat(),
        "buys_shares": total_buys_shares,
        "buys_value": total_buys_value,
        "sells_shares": total_sells_shares,
        "sells_value": total_sells_value,
        "net_shares": net_shares,
        "net_value": net_value
    }