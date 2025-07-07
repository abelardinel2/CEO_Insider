import requests
import json
from bs4 import BeautifulSoup
from parse_form4_xml import parse_form4_xml

SEC_HEADERS = {"User-Agent": "contact@oriadawn.xyz"}

def fetch_and_update_insider_flow(tickers):
    updated = {}

    for ticker, details in tickers.items():
        cik = details["cik"]
        print(f"🔍 Processing {ticker} with CIK {cik}")

        url = f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json"
        try:
            response = requests.get(url, headers=SEC_HEADERS)
            response.raise_for_status()
            data = response.json()

            alerts = []
            recent_filings = data.get("filings", {}).get("recent", {})
            forms = recent_filings.get("form", [])
            accession_numbers = recent_filings.get("accessionNumber", [])

            for form, acc_num in zip(forms, accession_numbers):
                if form == "4":
                    accession_clean = acc_num.replace("-", "")
                    index_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_clean}/{acc_num}-index.htm"
                    print(f"🔗 Found Form 4 index: {index_url}")

                    index_page = requests.get(index_url, headers=SEC_HEADERS).text
                    soup = BeautifulSoup(index_page, "html.parser")

                    xml_link = None
                    for a in soup.find_all("a", href=True):
                        if a["href"].endswith(".xml"):
                            xml_link = "https://www.sec.gov" + a["href"]
                            break

                    if xml_link:
                        print(f"📄 Fetching XML: {xml_link}")
                        xml_response = requests.get(xml_link, headers=SEC_HEADERS)
                        xml_response.raise_for_status()

                        parsed = parse_form4_xml(xml_response.text)

                        alert = {
                            "owner": parsed["reporting_owner"],
                            "type": "Buy" if parsed["transaction_code"] == "P" else "Sell",
                            "amount_buys": parsed["transaction_shares"],
                            "price_per_share": parsed["price_per_share"],
                            "link": index_url,
                            "xml_link": xml_link
                        }
                        alerts.append(alert)

            updated[ticker] = {
                "cik": cik,
                "buys": sum(1 for a in alerts if a["type"] == "Buy"),
                "sells": sum(1 for a in alerts if a["type"] == "Sell"),
                "alerts": alerts
            }

        except Exception as e:
            print(f"❌ Error fetching {ticker}: {e}")

    # ✅ Save final JSON
    with open("insider_flow.json", "w") as f:
        json.dump({"tickers": updated}, f, indent=2)
    print("✅ insider_flow.json updated with XML data")