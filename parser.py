import requests
from bs4 import BeautifulSoup
from datetime import datetime, date

def parse_form4_xml(url: str) -> dict:
    """
    ✅ Fully safe Form 4 parser: handles direct .xml, fallback index, skips double-dead links.
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
            print(f"❌ Direct XML failed, fallback to index")
            url = url.replace(".xml", "-index.htm")

    if not xml_soup:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            print(f"❌ Skipping: index page missing too: {url}")
            return None

        soup = BeautifulSoup(resp.text, "html.parser")
        xml_link = None
        for link in soup.find_all("a"):
            href = link.get("href", "")
            if href.endswith(".xml"):
                xml_link = href
                break

        if not xml_link:
            print(f"❌ Skipping: no .xml in index {url}")
            return None

        base = "/".join(url.split("/")[:-1])
        xml_url = f"{base}/{xml_link}"
        print(f"✅ Found real XML: {xml_url}")

        xml_soup = fetch_and_parse_xml(xml_url)
        if xml_soup is None:
            print(f"❌ Skipping: fallback XML failed too: {xml_url}")
            return None

    # ✅ Parse
    period_node = xml_soup.find("periodOfReport")
    if not period_node:
        return None

    filing_dt = datetime.strptime(period_node.text, "%Y-%m-%d").date()
    if (date.today() - filing_dt).days > 7:
        return None

    total_buys_shares = total_sells_shares = 0
    total_buys_value = total_sells_value = 0

    for txn in xml_soup.find_all("nonDerivativeTransaction"):
        code = txn.transactionCode.string if txn.transactionCode else ""
        amount = float(txn.find("transactionShares").value.string or 0) if txn.find("transactionShares") else 0
        price = float(txn.find("transactionPricePerShare").value.string or 0) if txn.find("transactionPricePerShare") else 0

        if code in ["P", "A", "M", "C"]:
            total_buys_shares += amount
            total_buys_value += amount * price
        elif code == "S":
            total_sells_shares += amount
            total_sells_value += amount * price

    for txn in xml_soup.find_all("derivativeTransaction"):
        code = txn.transactionCode.string if txn.transactionCode else ""
        amount = float(txn.find("transactionShares").value.string or 0) if txn.find("transactionShares") else 0
        price = float(txn.find("transactionPricePerShare").value.string or 0) if txn.find("transactionPricePerShare") else 0

        if code in ["P", "A", "M", "C"]:
            total_buys_shares += amount
            total_buys_value += amount * price
        elif code == "S":
            total_sells_shares += amount
            total_sells_value += amount * price

    net_shares = total_buys_shares - total_sells_shares
    net_value = total_buys_value - total_sells_value

    print(f"✅ Done: buys={total_buys_shares} sells={total_sells_shares} net={net_shares}")
    return {
        "date": filing_dt.isoformat(),
        "buys_shares": total_buys_shares,
        "buys_value": total_buys_value,
        "sells_shares": total_sells_shares,
        "sells_value": total_sells_value,
        "net_shares": net_shares,
        "net_value": net_value
    }