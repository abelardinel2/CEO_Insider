import requests
import json
from lxml import etree
from datetime import datetime

SEC_HEADERS = {"User-Agent": "contact@oriadawn.xyz"}

def fetch_and_update_insider_flow(tickers):
    updated = {}

    for ticker, details in tickers.items():
        cik = details["cik"]
        print(f"🔍 Processing {ticker} with CIK {cik}")

        submissions_url = f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json"
        try:
            resp = requests.get(submissions_url, headers=SEC_HEADERS, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            recent = data.get("filings", {}).get("recent", {})
            forms = recent.get("form", [])
            accession_numbers = recent.get("accessionNumber", [])
            filing_dates = recent.get("filingDate", [])

            alerts = []
            seen = set()

            for form, acc_num, filing_date in zip(forms, accession_numbers, filing_dates):
                if form == "4":
                    filing_dt = datetime.strptime(filing_date, "%Y-%m-%d").date()
                    if (datetime.utcnow().date() - filing_dt).days > 7:
                        continue

                    index_url = (
                        f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_num.replace('-', '')}/{acc_num}-index.htm"
                    )
                    xml_url = (
                        f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_num.replace('-', '')}/"
                        f"form4_{acc_num.replace('-', '')}.xml"
                    )
                    print(f"🔗 Found Form 4 index: {index_url}")
                    print(f"📄 Fetching XML: {xml_url}")

                    xml_resp = requests.get(xml_url, headers=SEC_HEADERS, timeout=10)
                    if xml_resp.status_code == 200:
                        try:
                            owner, shares = parse_form4_xml(xml_resp.text)
                            if acc_num not in seen:
                                alerts.append({
                                    "owner": owner,
                                    "type": "Buy",
                                    "amount_buys": shares,
                                    "link": index_url
                                })
                                seen.add(acc_num)
                        except Exception as e:
                            print(f"❌ Error parsing XML for {ticker}: {e}")
                    else:
                        print(f"❌ XML not found for {ticker}: {xml_url}")

            updated[ticker] = {
                "cik": cik,
                "buys": len(alerts),
                "sells": 0,
                "alerts": alerts
            }

        except Exception as e:
            print(f"❌ Error fetching {ticker}: {e}")

    with open("insider_flow.json", "w") as f:
        json.dump({"tickers": updated}, f, indent=2)
    print("✅ insider_flow.json updated with deduped alerts")

def parse_form4_xml(xml_content):
    parser = etree.XMLParser(recover=True)
    root = etree.fromstring(xml_content.encode(), parser=parser)

    ns = {"ns": root.nsmap[None]} if None in root.nsmap else {}

    def find_text(xpath):
        result = root.xpath(xpath, namespaces=ns)
        return result[0].text.strip() if result else "N/A"

    owner = find_text(".//reportingOwner/reportingOwnerId/rptOwnerName")
    shares = find_text(".//nonDerivativeTable/nonDerivativeTransaction/transactionAmounts/transactionShares/value")

    return owner, shares