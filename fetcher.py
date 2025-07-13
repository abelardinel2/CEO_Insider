import requests
from datetime import datetime, timedelta
import time
import logging

# Configure logging
logging.basicConfig(
    filename="edgar_errors.log",
    level=logging.INFO,  # Changed to INFO to log zero Form 4s
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def fetch_recent_form4_urls(cik):
    urls = []
    today = datetime.utcnow()
    cutoff = today - timedelta(days=14)

    index_url = f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json"
    headers = {"User-Agent": "Oria Dawn Analytics contact@oriadawn.xyz"}

    try:
        time.sleep(0.1)  # SEC rate limit: 100ms
        r = requests.get(index_url, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        recent = data.get("filings", {}).get("recent", {})
        accession_numbers = recent.get("accessionNumber", [])
        forms = recent.get("form", [])
        filing_dates = recent.get("filingDate", [])
        primary_docs = recent.get("primaryDocument", [])

        for i, form_type in enumerate(forms):
            if form_type == "4" and i < len(filing_dates) and i < len(primary_docs):
                date = datetime.strptime(filing_dates[i], "%Y-%m-%d")
                if date >= cutoff:
                    accession = accession_numbers[i].replace("-", "")
                    primary_doc = primary_docs[i] if i < len(primary_docs) else None
                    if primary_doc:
                        url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{primary_doc}"
                        urls.append(url)
                    else:
                        logging.error(f"No primaryDocument for CIK {cik}, accession {accession_numbers[i]}")
        if not urls:
            logging.info(f"No Form 4 filings found for CIK {cik} within last 14 days")
        else:
            logging.info(f"Found {len(urls)} Form 4 URLs for CIK {cik}")
        print(f"📡 Found {len(urls)} Form 4 URLs for CIK {cik}")
    except Exception as e:
        logging.error(f"Error fetching CIK {cik}: {str(e)}")
        print(f"❌ Error fetching CIK {cik}: {e}")

    return urls