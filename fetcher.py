import requests
import json
from parse_form4_xml import parse_form4_xml  # ✅ use your existing parser
from datetime import datetime

SEC_HEADERS = {"User-Agent": "contact@oriadawn.xyz"}

def fetch_and_update_insider_flow(tickers):
    updated = {}

    for ticker, details in tickers.items():
        cik = details["cik"]
        print(f"Processing {ticker} with CIK {cik}")

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
                    # 🧩 Build XML URL
                    acc_clean = acc_num.replace("-", "")
                    xml_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_clean}/xslF345X03/primary_doc.xml"

                    print(f"🔍 Fetching XML: {xml_url}")
                    xml_resp = requests.get(xml_url, headers=SEC_HEADERS)
                    xml_resp.raise_for_status()

                    parsed = parse_form4_xml(xml_resp.text)

                    shares = float(parsed["transaction_shares"]) if parsed["transaction_shares"] != "N/A" else 0
                    tx_code = parsed["transaction_code"]

                    if tx_code == "P" or tx_code == "A":
                        buys = shares
                        sells = 0
                        trade_type = "Buy"
                        bias = "🤑💰 Insider Accumulation"
                    elif tx_code == "S" or tx_code == "D":
                        buys = 0
                        sells = shares
                        trade_type = "Sell"
                        bias = "💩🚽 Insider Dump"
                    else:
                        continue  # skip unknown types

                    link = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_clean}/{acc_num}-index.htm"

                    alert = {
                        "owner": parsed["reporting_owner"],
                        "type": trade_type,
                        "amount_buys": buys,
                        "amount_sells": sells,
                        "bias": bias,
                        "link": link
                    }

                    alerts.append(alert)

            updated[ticker] = {
                "cik": cik,
                "buys": sum(a["amount_buys"] for a in alerts),
                "sells": sum(a["amount_sells"] for a in alerts),
                "alerts": alerts
            }

        except Exception as e:
            print(f"❌ Error fetching {ticker}: {e}")

    with open("insider_flow.json", "w") as f:
        json.dump({"tickers": updated}, f, indent=2)
    print("✅ insider_flow.json updated with real XML data")