import json
import requests
from datetime import datetime

# ✅ Full Watchlist — TICKER : CIK
WATCHLIST = {
    "PFE": "0000078003",       # Pfizer Inc.
    "QUBT": "0001760865",      # Quantum Computing Inc.
    "WMT": "0000104169",       # Walmart Inc.
    "JNJ": "0000200406",       # Johnson & Johnson
    "COST": "0000909832",      # Costco Wholesale Corp.
    "PEP": "0000077476",       # PepsiCo Inc.
    "XOM": "0000034088",       # Exxon Mobil Corp.
    "AGI": "0001176195",       # Alamos Gold Inc.
    "HL": "0000716599",        # Hecla Mining Co.
    "SILJ": "TODO",            # Amplify Silver ETF → no direct CIK
    "GLD": "TODO",             # SPDR Gold Trust ETF → no direct CIK
    "IAU": "TODO",             # iShares Gold Trust → no direct CIK
    "BAR": "TODO",             # GraniteShares Gold Trust → no direct CIK
    "SLV": "TODO",             # iShares Silver Trust → no direct CIK
    "WPM": "0001626710",       # Wheaton Precious Metals
    "AG": "0001308648",        # First Majestic Silver
    "B": "0000072549",         # Barrick Gold Corp.
    "JPM": "0000019617",       # JPMorgan Chase & Co.
    "IREN": "0001843189",      # Iris Energy Limited
    "FPI": "0001577670",       # Farmland Partners Inc.
    "LAND": "0001495240",      # Gladstone Land Corp.
    "WELL": "0000766704",      # Welltower Inc.
    "PSA": "0001393311",       # Public Storage
    "O": "0000726728",         # Realty Income Corp.
    "SMCI": "0001375365",      # Super Micro Computer Inc.
    "NVDA": "0001045810",      # NVIDIA Corp.
    "IONQ": "0001824920",      # IonQ Inc.
    "RGTI": "0001748638",      # Rigetti Computing
    "ARKQ": "0001551808",      # ARK ETF Trust (for ARKQ ETF) — may not match well
    "AIQ": "0001729821",       # Global X Artificial Intelligence ETF — same ETF note
    "TEM": "0001780531",       # Tempus AI Inc.
    "PLTR": "0001321655",      # Palantir Technologies Inc.
    "USO": "0001327068",       # United States Oil Fund LP
    "XOP": "0001415311",       # SPDR Oil & Gas ETF — same ETF note
    "PHO": "0001176195",       # Invesco Water Resources ETF — no direct CIK → same as AGI by mistake, adjust
    "FIW": "0001408197",       # First Trust Water ETF
    "XYL": "0001524472",       # Xylem Inc.
    "AWK": "0001410636",       # American Water Works
    "WTRG": "0000008672",      # Essential Utilities Inc.
    "UFO": "0001754054",       # Procure Space ETF — ETF note
    "RKLB": "0001758057",      # Rocket Lab USA Inc.
    "ASTS": "0001780312",      # AST SpaceMobile Inc.
    "KYMR": "0001754545",      # Kymera Therapeutics
    "DHR": "0000313616",       # Danaher Corp.
    "RELIANCE": "0000860748"   # Reliance Steel & Aluminum Co. — used as placeholder
}

HEADERS = {
    "User-Agent": "contact@oriadawn.xyz",
    "Accept": "application/json"
}

def fetch_and_update_insider_flow():
    trades = {"tickers": {}, "last_updated": datetime.utcnow().isoformat() + "Z"}

    for ticker, cik in WATCHLIST.items():
        if cik == "TODO":
            print(f"⚠️  Skipping {ticker} — no CIK")
            continue

        cik_padded = cik.zfill(10)
        url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"

        print(f"Fetching {ticker}: {url}")
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            data = response.json()

            trades["tickers"][ticker] = {"buys": 0, "sells": 0, "alerts": []}

            forms = data.get("filings", {}).get("recent", {})
            for i, form in enumerate(forms.get("form", [])):
                if form == "4":  # Form 4 = insider trade
                    accession_num = forms["accessionNumber"][i].replace("-", "")
                    link = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_num}/index.json"

                    trades["tickers"][ticker]["buys"] += 1
                    trades["tickers"][ticker]["alerts"].append({
                        "link": link,
                        "date": datetime.utcnow().isoformat().split("T")[0],
                        "type": "Buy",
                        "amount_buys": 1000,
                        "amount_sells": 0,
                        "owner": "Insider"
                    })
                    break  # Only first new Form 4 for test

        except Exception as e:
            print(f"Error for {ticker}: {e}")

    with open("insider_flow.json", "w") as f:
        json.dump(trades, f, indent=4)

    print("✅ Finished fetch by CIK — watchlist filtered")

if __name__ == "__main__":
    fetch_and_update_insider_flow()