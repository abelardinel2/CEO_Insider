import os
import requests
import xml.etree.ElementTree as ET
import json
from datetime import datetime

WATCHLIST = {
    "PFE": "0000078003",
    "QUBT": "0001593219",
    "WMT": "0000104169",
    "JNJ": "0000200406",
    "COST": "0000909832",
    "PEP": "0000077476",
    "XOM": "0000034088",
    "AGI": "0001072725",
    "HL": "0000716592",
    "SILJ": "0001526815",
    "GLD": "0001222333",
    "IAU": "0001278680",
    "BAR": "0001571049",
    "SLV": "0001330568",
    "WPM": "0001626890",
    "AG": "0001308648",
    "B": "0000072541",
    "COIN": "0001679788",
    "JPM": "0000019617",
    "IREN": "0001841968",
    "FPI": "0001591670",
    "LAND": "0001527541",
    "WELL": "0000766704",
    "PSA": "0001393311",
    "O": "0000726728",
    "SMCI": "0001375365",
    "NVDA": "0001045810",
    "IONQ": "0001824920",
    "RGTI": "0001866692",
    "ARKQ": "0001597742",
    "AIQ": "0001760175",
    "PLTR": "0001321655",
    "USO": "0001327068",
    "XOP": "0001160308",
    "PHO": "0001398432",
    "FIW": "0001398518",
    "XYL": "0001524472",
    "AWK": "0001410636",
    "WTRG": "0000078319",
    "UFO": "0001751245",
    "RKLB": "0001836833",
    "ASTS": "0001780312",
    "KYMR": "0001824293",
    "DHR": "0000885160",
    "RELIANCE": "0000081381"
}

def fetch_and_update_insider_flow():
    url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent"
    headers = {
        "User-Agent": "Mozilla/5.0 (CEOInsiderBot/1.0 contact@oriadawn.xyz)",
        "Accept": "application/xml"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        trades = {
            "tickers": {ticker: {"buys": 0, "sells": 0, "alerts": []} for ticker in WATCHLIST},
            "last_updated": datetime.utcnow().isoformat() + "Z"
        }

        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            link_el = entry.find("{http://www.w3.org/2005/Atom}link")
            link = link_el.attrib.get('href') if link_el is not None else ""

            if "/edgar/data/" in link:
                cik = link.split("/edgar/data/")[1].split("/")[0].strip()
                for ticker, watch_cik in WATCHLIST.items():
                    if watch_cik != "NA" and cik == watch_cik:
                        trades["tickers"][ticker]["buys"] += 1000  # Placeholder
                        trades["tickers"][ticker]["alerts"].append({
                            "link": link,
                            "date": datetime.utcnow().isoformat().split("T")[0],
                            "type": "Buy",
                            "amount_buys": 1000
                        })
                        print(f"✅ Matched {ticker} → {cik}")

        with open("insider_flow.json", "w") as f:
            json.dump(trades, f, indent=4)

        print("✅ insider_flow.json updated")

    except Exception as e:
        print(f"❌ Fetcher error: {e}")

if __name__ == "__main__":
    fetch_and_update_insider_flow()