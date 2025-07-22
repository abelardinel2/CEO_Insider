import requests
from datetime import datetime, timedelta

HEADERS = {
    "User-Agent": "OriaDawnAnalytics/1.0 contact@oriadawn.xyz"
}

def pad_cik(cik):
    return str(cik).zfill(10)

def fetch_recent_form4(cik):
    url = f"https://data.sec.gov/submissions/CIK{pad_cik(cik)}.json"
    try:
        r = requests.get(url, headers=HEADERS)
        data = r.json()
        results = []

        if "filings" in data and "recent" in data["filings"]:
            filings = data["filings"]["recent"]
            for i in range(len(filings["accessionNumber"])):
                if filings["form"][i] == "4":
                    filed_date = datetime.strptime(filings["filingDate"][i], "%Y-%m-%d")
                    if filed_date >= datetime.today() - timedelta(days=7):
                        results.append({
                            "owner": filings["reportingOwner"][i],
                            "type": filings["form"][i],
                            "amount": filings.get("transactionShares", ["?"])[i],
                            "bias": "Buy 🟢" if "A" in filings["transactionCodes"][i] else "Sell 🔴",
                            "link": f"https://www.sec.gov/Archives/edgar/data/{pad_cik(cik)}/{filings['accessionNumber'][i].replace('-', '')}/index.json",
                            "filed": filings["filingDate"][i]
                        })
        return results

    except Exception as e:
        print(f"Error fetching data for CIK {cik}: {e}")
        return []