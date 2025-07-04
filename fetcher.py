import json
import requests
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 OriaBot (contact@oriadawn.xyz)"
}

def fetch_watchlist_filings():
    """
    Original: Updates insider_flow.json with simple counts.
    Optional: keep if you want JSON logs.
    """
    with open("cik_watchlist.json", "r") as f:
        cik_data = json.load(f)

    trades = {
        "tickers": {},
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }

    for _, info in cik_data.items():
        cik = str(info["cik_str"]).zfill(10)
        ticker = info["ticker"]

        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        print(f"Fetching {ticker}: {url}")

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()

            recent = data.get("filings", {}).get("recent", {})
            form_types = recent.get("form", [])

            buys = sells = 0
            alerts = []

            for idx, form_type in enumerate(form_types):
                if form_type == "4":
                    transaction = {
                        "date": recent["filingDate"][idx],
                        "link": f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{recent['accessionNumber'][idx].replace('-', '')}/{recent['accessionNumber'][idx]}-index.htm",
                        "type": "Buy",
                        "amount_buys": 1000,  # Placeholder for simple JSON log
                        "amount_sells": 0
                    }
                    buys += 1
                    alerts.append(transaction)

            trades["tickers"][ticker] = {
                "buys": buys,
                "sells": sells,
                "alerts": alerts
            }

        except Exception as e:
            print(f"❌ Error fetching {ticker}: {e}")

    with open("insider_flow.json", "w") as f:
        json.dump(trades, f, indent=2)
    print("✅ insider_flow.json updated.")


def get_recent_form4_urls():
    """
    New: This is what `main.py` imports.
    Returns a list of `.xml` Form 4 links ONLY from last 7 days.
    """
    with open("cik_watchlist.json", "r") as f:
        cik_data = json.load(f)

    urls = []

    for _, info in cik_data.items():
        cik = str(info["cik_str"]).zfill(10)
        ticker = info["ticker"]

        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        print(f"Checking {ticker}: {url}")

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()

            recent = data.get("filings", {}).get("recent", {})
            form_types = recent.get("form", [])
            filing_dates = recent.get("filingDate", [])
            accessions = recent.get("accessionNumber", [])

            for idx, form_type in enumerate(form_types):
                if form_type == "4":
                    filing_date = filing_dates[idx]
                    filing_dt = datetime.strptime(filing_date, "%Y-%m-%d").date()
                    today = datetime.utcnow().date()

                    if (today - filing_dt).days <= 7:
                        # Build direct .xml link
                        accession_clean = accessions[idx].replace("-", "")
                        link = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_clean}/{accessions[idx]}.xml"
                        urls.append(link)

        except Exception as e:
            print(f"❌ Error fetching {ticker}: {e}")

    print(f"✅ Total recent Form 4 XMLs found: {len(urls)}")
    return urls


if __name__ == "__main__":
    fetch_watchlist_filings()