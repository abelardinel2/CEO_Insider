import os
import requests
import xml.etree.ElementTree as ET
import json
from datetime import datetime

# ✅ Your watchlist mapped with CIKs (double-check or update any ?)
WATCHLIST = {
    "PFE": "0000078003",  # Pfizer
    "QUBT": "0001593219",  # Quantum Computing Inc
    "WMT": "0000104169",  # Walmart
    "JNJ": "0000200406",  # Johnson & Johnson
    "COST": "0000909832",  # Costco
    "PEP": "0000077476",  # PepsiCo
    "XOM": "0000034088",  # Exxon Mobil
    "AGI": "0001072725",  # Alamos Gold Inc
    "HL": "0000716592",  # Hecla Mining
    "SILJ": "0001526815",  # ETFMG Prime Junior Silver Miners ETF (note: ETF)
    "GLD": "0001222333",  # SPDR Gold Trust ETF
    "IAU": "0001278680",  # iShares Gold Trust ETF
    "BAR": "0001571049",  # GraniteShares Gold Trust (BAR ETF)
    "SLV": "0001330568",  # iShares Silver Trust
    "WPM": "0001626890",  # Wheaton Precious Metals
    "AG": "0001308648",  # First Majestic Silver
    "B": "0000072541",  # Barrick Gold
    "XAGUSD": "NA",  # Silver spot — won't have SEC filings
    "COIN": "0001679788",  # Coinbase
    "JPM": "0000019617",  # JPMorgan Chase
    "IREN": "0001841968",  # Iris Energy
    "FPI": "0001591670",  # Farmland Partners
    "LAND": "0001527541",  # Gladstone Land
    "WELL": "0000766704",  # Welltower Inc
    "PSA": "0001393311",  # Public Storage
    "O": "0000726728",  # Realty Income Corp
    "SMCI": "0001375365",  # Super Micro Computer
    "NVDA": "0001045810",  # Nvidia
    "IONQ": "0001824920",  # IonQ Inc
    "RGTI": "0001866692",  # Rigetti Computing
    "ARKQ": "0001597742",  # ARK Autonomous Tech ETF (ETF)
    "AIQ": "0001760175",  # Global X Artificial Intelligence ETF (ETF)
    "TEM": "?",  # Not clear, please verify
    "PLTR": "0001321655",  # Palantir
    "USO": "0001327068",  # United States Oil Fund (ETF)
    "XOP": "0001160308",  # SPDR Oil & Gas ETF
    "PHO": "0001398432",  # Invesco Water Resources ETF
    "FIW": "0001398518",  # First Trust Water ETF
    "XYL": "0001524472",  # Xylem Inc
    "AWK": "0001410636",  # American Water Works
    "WTRG": "0000078319",  # Essential Utilities
    "UFO": "0001751245",  # Procure Space ETF
    "RKLB": "0001836833",  # Rocket Lab
    "ASTS": "0001780312",  # AST SpaceMobile
    "BTCUSD": "NA",  # Bitcoin spot — no SEC CIK
    "ETHUSD": "NA",  # Ethereum spot — no SEC CIK
    "XRPUSD": "NA",  # Ripple — no SEC CIK
    "SUIUSD": "NA",  # Sui token — no SEC CIK
    "KYMR": "0001824293",  # Kymera Therapeutics
    "DHR": "0000885160",  # Danaher Corp
    "RELIANCE": "0000081381"  # Reliance Steel & Aluminum
}

def fetch_and_update_insider_flow():
    url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; CEOInsiderBot/1.0; +contact@oriadawn.xyz)",
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
            link = link_el.attrib['href'] if link_el is not None else ""
            cik = link.split("/edgar/data/")[1].split("/")[0] if "/edgar/data/" in link else None

            if cik:
                for ticker, watch_cik in WATCHLIST.items():
                    if cik == watch_cik:
                        # Example: fake buy signal
                        trades["tickers"][ticker]["buys"] += 1000
                        trades["tickers"][ticker]["alerts"].append({
                            "link": link,
                            "date": datetime.utcnow().isoformat().split("T")[0],
                            "type": "Buy",
                            "amount_buys": 1000
                        })
                        print(f"✅ Matched {ticker} (CIK {cik})")

        with open("insider_flow.json", "w") as f:
            json.dump(trades, f, indent=4)

        print("✅ Insider flow updated.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fetch_and_update_insider_flow()