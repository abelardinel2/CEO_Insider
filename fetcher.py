import os
import requests
import xml.etree.ElementTree as ET
import json
import re
from datetime import datetime, timedelta

# ✅ Final watchlist with direct CIKs — only real companies
WATCHLIST_CIKS = {
    "PFE": "78003",
    "QUBT": "1675180",
    "WMT": "104169",
    "JNJ": "200406",
    "COST": "909832",
    "PEP": "77476",
    "XOM": "34088",
    "AGI": "1591308",      # Alamos Gold
    "HL": "719413",        # Hecla Mining
    "GLD": "1222333",      # SPDR Gold Trust (still included if you like)
    "IAU": "1278680",      # iShares Gold Trust (still included if you like)
    "BAR": "1598477",      # GraniteShares Gold Trust
    "SLV": "1330567",      # iShares Silver Trust
    "WPM": "1656081",      # Wheaton Precious Metals
    "AG": "1437174",       # First Majestic Silver
    "GOLD": "756894",      # Barrick Gold Corporation
    "COIN": "1679788",
    "JPM": "19617",
    "IREN": "1843181",
    "FPI": "1591670",
    "LAND": "1495240",
    "WELL": "766704",
    "PSA": "1393311",
    "O": "726728",
    "SMCI": "1375365",
    "NVDA": "1045810",
    "IONQ": "1824920",
    "RGTI": "1863097",
    "PLTR": "1321655",
    "USO": "1327068",
    "XYL": "1524472",
    "AWK": "1410636",
    "WTRG": "78128",
    "RKLB": "1819999",
    "ASTS": "1780312",
    "KYMR": "1788028",
    "DHR": "313616"
}

# ✅ Dummy parse for Form 4 XML — replace with real parsing later
def parse_form4_xml(link):
    # You’ll replace this with your real Form 4 parser!
    return {"buys": 1000, "sells": 0}

def fetch_and_update_insider_flow():
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    date_format = "%Y%m%d"

    url = (
        f"https://www.sec.gov/cgi-bin/browse-edgar?"
        f"action=getcurrent&dateb={start_date.strftime(date_format)}"
        f"&datea={end_date.strftime(date_format)}&type=4&owner=include&output=atom"
    )

    print(f"✅ Using SEC URL: {url}")

    headers = {
        "User-Agent": "Mozilla/5.0 (contact@oriadawn.xyz)",
        "Accept": "application/xml"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"✅ Fetched SEC feed: {response.status_code}")

        root = ET.fromstring(response.content)

        trades = {
            "tickers": {ticker: {"buys": 0, "sells": 0, "alerts": []} for ticker in WATCHLIST_CIKS.keys()},
            "last_updated": datetime.utcnow().isoformat() + "Z"
        }

        for item in root.findall('{http://www.w3.org/2005/Atom}entry'):
            link = item.find('{http://www.w3.org/2005/Atom}link')['href']
            m = re.search(r'/data/(\d+)/', link)
            if not m:
                continue

            cik = m.group(1).lstrip("0")
            ticker = next((k for k, v in WATCHLIST_CIKS.items() if v == cik), None)

            if ticker:
                print(f"✅ Matched: {ticker} (CIK {cik}) → {link}")
                try:
                    form4_data = parse_form4_xml(link)
                    if not form4_data or "buys" not in form4_data:
                        continue
                    trades["tickers"][ticker]["buys"] += form4_data["buys"]
                    trades["tickers"][ticker]["sells"] += form4_data["sells"]

                    if form4_data["buys"] > 0 or form4_data["sells"] > 0:
                        trades["tickers"][ticker]["alerts"].append({
                            "link": link,
                            "date": datetime.utcnow().isoformat().split("T")[0],
                            "type": "Buy" if form4_data["buys"] > 0 else "Sell",
                            "amount_buys": form4_data["buys"],
                            "amount_sells": form4_data["sells"],
                            "owner": "Insider"
                        })

                except Exception as e:
                    print(f"⚠️ Parse failed for {link}: {e}")

        with open("insider_flow.json", "w") as f:
            json.dump(trades, f, indent=4)
        print("✅ insider_flow.json saved!")

    except Exception as e:
        print(f"❌ Fetch error: {e}")

if __name__ == "__main__":
    fetch_and_update_insider_flow()