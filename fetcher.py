import os
import requests
import json
from datetime import datetime, timedelta

CIK_WATCHLIST = {
    "PFE": 78003,
    "QUBT": 1775285,
    "WMT": 104169,
    "JNJ": 200406,
    "COST": 909832,
    "PEP": 77476,
    "XOM": 34088,
    "AGI": 1388141,
    "HL": 719413,
    "GLD": 1222333,
    "IAU": 1327068,
    "SLV": 1330568,
    "WPM": 1048805,
    "AG": 1437174,
    "GOLD": 756894,
    "COIN": 1679788,
    "JPM": 19617,
    "IREN": 1845815,
    "FPI": 1591670,
    "LAND": 1495240,
    "WELL": 766704,
    "PSA": 1393311,
    "O": 726728,
    "SMCI": 1375365,
    "NVDA": 1045810,
    "IONQ": 1824920,
    "RGTI": 1837518,
    "ARKQ": 1577526,
    "AIQ": 1454889,
    "PLTR": 1321655,
    "USO": 1327068,
    "XOP": 1327068,
    "PHO": 1277227,
    "FIW": 1400893,
    "XYL": 1524472,
    "AWK": 1410636,
    "WTRG": 86729,
    "UFO": 1754057,
    "RKLB": 1819994,
    "ASTS": 1780312,
    "KYMR": 1722879,
    "DHR": 313616,
    "RELIANCE": 0  # placeholder if needed
}

def fetch_and_update_insider_flow():
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)

    for ticker, cik in CIK_WATCHLIST.items():
        if cik == 0:
            continue

        cik_str = str(cik).zfill(10)
        url = f"https://data.sec.gov/submissions/CIK{cik_str}.json"

        headers = {
            "User-Agent": "Mozilla/5.0 (youremail@domain.com)"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            print(f"✅ Fetched: {url}")

            data = response.json()
            with open(f"{ticker}_insider.json", "w") as f:
                json.dump(data, f, indent=2)

        except requests.RequestException as e:
            print(f"❌ Error fetching {ticker}: {e}")

if __name__ == "__main__":
    fetch_and_update_insider_flow()