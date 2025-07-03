import os
import requests
import xml.etree.ElementTree as ET
import json
from datetime import datetime, timedelta

# ✅ Your CLEANED WATCHLIST (no crypto)
WATCHLIST = [
    "PFE", "QUBT", "WMT", "JNJ", "COST", "PEP", "XOM", "AGI", "HL", "SILJ", "GLD",
    "IAU", "BAR", "SLV", "WPM", "AG", "B", "COIN", "JPM", "IREN", "FPI", "LAND",
    "WELL", "PSA", "O", "SMCI", "NVDA", "IONQ", "RGTI", "ARKQ", "AIQ", "TEM", "PLTR",
    "USO", "XOP", "PHO", "FIW", "XYL", "AWK", "WTRG", "UFO", "RKLB", "ASTS", "KYMR",
    "DHR", "RELIANCE"
]

# ✅ YOUR INLINE PARSER — replace with your real version!
def parse_form4_xml(link):
    try:
        headers = {"User-Agent": "OriaDawnBot (contact@oriadawn.xyz)"}
        resp = requests.get(link, headers=headers, timeout=10)
        resp.raise_for_status()

        soup = ET.fromstring(resp.content)

        owner = "Unknown Insider"
        owner_tag = soup.find(".//rptOwnerName")
        if owner_tag is not None:
            owner = owner_tag.text

        buys = sells = 0

        for txn in soup.findall(".//nonDerivativeTransaction"):
            code = txn.findtext("transactionCode") or ""
            acquired_or_disposed = txn.findtext("transactionAcquiredDisposedCode") or ""
            amount_node = txn.find(".//transactionShares")
            amount = float(amount_node.findtext("value")) if amount_node is not None else 0

            if code == "P" or acquired_or_disposed == "A":
                buys += amount
            elif code == "S" or acquired_or_disposed == "D":
                sells += amount

        return {"buys": buys, "sells": sells, "owner": owner}

    except Exception as e:
        print(f"❌ Error parsing Form 4 XML: {e}")
        return {"buys": 0, "sells": 0, "owner": "Unknown"}

def fetch_and_update_insider_flow():
    # ✅ Use a polite RSS instead of a bad CSV
    url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=4&owner=include&output=atom"
    headers = {
        "User-Agent": "OriaDawnBot (contact@oriadawn.xyz)",
        "Accept": "application/xml"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"✅ Fetched RSS at {datetime.now()}")

        root = ET.fromstring(response.content)
        trades = {
            "tickers": {ticker: {"buys": 0, "sells": 0, "alerts": []} for ticker in WATCHLIST},
            "last_updated": datetime.utcnow().isoformat() + "Z"
        }

        for item in root.findall('{http://www.w3.org/2005/Atom}entry'):
            title = item.find('{http://www.w3.org/2005/Atom}title').text or ""
            summary = item.find('{http://www.w3.org/2005/Atom}summary').text or ""
            link = item.find('{http://www.w3.org/2005/Atom}link').attrib['href']
            print(f"🔗 Processing: {link}")

            for ticker in WATCHLIST:
                if ticker in title.upper() or ticker in summary.upper():
                    form4_data = parse_form4_xml(link)

                    trades["tickers"][ticker]["buys"] += form4_data["buys"]
                    trades["tickers"][ticker]["sells"] += form4_data["sells"]

                    if form4_data["buys"] > 0 or form4_data["sells"] > 0:
                        trades["tickers"][ticker]["alerts"].append({
                            "link": link,
                            "date": datetime.utcnow().isoformat().split("T")[0],
                            "type": "Buy" if form4_data["buys"] > 0 else "Sell",
                            "amount_buys": form4_data["buys"],
                            "amount_sells": form4_data["sells"],
                            "owner": form4_data.get("owner", "Insider")
                        })

        print(f"✅ Trade summary: {trades}")

        with open("insider_flow.json", "w") as f:
            json.dump(trades, f, indent=4)

        with open("output.log", "a") as f:
            f.write(f"{datetime.now()} - Fetch completed: {trades}\n")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching data: {e}")
        with open("insider_flow.json", "w") as f:
            json.dump({"tickers": {ticker: {"buys": 0, "sells": 0, "alerts": []} for ticker in WATCHLIST},
                       "last_updated": datetime.utcnow().isoformat() + "Z"}, f, indent=4)
        with open("output.log", "a") as f:
            f.write(f"{datetime.now()} - Fetch failed: {e}\n")

    except ET.ParseError as e:
        print(f"❌ XML Parse Error: {e}")
        with open("insider_flow.json", "w") as f:
            json.dump({"tickers": {ticker: {"buys": 0, "sells": 0, "alerts": []} for ticker in WATCHLIST},
                       "last_updated": datetime.utcnow().isoformat() + "Z"}, f, indent=4)
        with open("output.log", "a") as f:
            f.write(f"{datetime.now()} - Parse error: {e}\n")

if __name__ == "__main__":
    fetch_and_update_insider_flow()