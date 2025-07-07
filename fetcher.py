import requests
import json

def get_doc4_xml_url(cik):
    base_url = f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json"
    headers = {"User-Agent": "contact@oriadawn.xyz"}
    response = requests.get(base_url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching {cik}: {response.status_code}")
        return None

    data = response.json()
    forms = data.get("filings", {}).get("recent", {})
    accession_numbers = forms.get("accessionNumber", [])
    form_types = forms.get("form", [])

    for i, form_type in enumerate(form_types):
        if form_type == "4":
            acc = accession_numbers[i].replace("-", "")
            xml_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/doc4.xml"
            return xml_url

    return None

def fetch_and_update_insider_flow(tickers):
    for ticker, info in tickers.items():
        cik = info["cik"]
        print(f"Processing {ticker} with CIK {cik}")
        url = get_doc4_xml_url(cik)
        if url:
            print(f"✅ Found URL: {url}")
        else:
            print(f"❌ No Form 4 found for {ticker} ({cik})")