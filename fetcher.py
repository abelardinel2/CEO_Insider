import requests
from datetime import datetime, timedelta

def fetch_recent_form4_urls(cik):
    urls = []
    today = datetime.utcnow()
    cutoff = today - timedelta(days=14)

    index_url = f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json"
    headers = {"User-Agent": "Oria Dawn Analytics contact@oriadawn.xyz"}

    try:
        r = requests.get(index_url, headers=headers)
        data = r.json()
        recent = data.get("filings", {}).get("recent", {})
        accession_numbers = recent.get("accessionNumber", [])
        forms = recent.get("form", [])
        filing_dates = recent.get("filingDate", [])

        for i, form_type in enumerate(forms):
            if form_type == "4":
                date = datetime.strptime(filing_dates[i], "%Y-%m-%d")
                if date >= cutoff:
                    accession = accession_numbers[i].replace("-", "")
                    url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/xslF345X03/doc1.xml"
                    urls.append(url)
    except Exception as e:
        print(f"❌ Error fetching CIK {cik}: {e}")

    return urls