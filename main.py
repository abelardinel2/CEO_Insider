import json
import requests
from datetime import datetime, timedelta
from parse_form4_txt import parse_form4_txt

# Load CIK watchlist
with open("cik_watchlist.json", "r") as f:
    tickers = json.load(f)["tickers"]

alerts = []
headers = {"User-Agent": "insider-tracker"}

for ticker, info in tickers.items():
    cik = info["cik"]
    cik_str = str(cik).zfill(10)
    print(f"🔍 Checking {ticker} (CIK {cik})")

    try:
        # Fetch company submissions
        url = f"https://data.sec.gov/submissions/CIK{cik_str}.json"
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        print(f"❌ Fetch error for {ticker}: {e}")
        continue

    filings = data.get("filings", {}).get("recent", {})
    accession_numbers = filings.get("accessionNumber", [])
    form_types = filings.get("form", [])
    filing_dates = filings.get("filingDate", [])

    if not accession_numbers:
        print(f"⚠️ No filings found for {ticker}")
        continue

    for acc_no, form, date_str in zip(accession_numbers, form_types, filing_dates):
        if form != "4":
            continue

        # Filter by date (last 14 days)
        try:
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            if file_date < datetime.now() - timedelta(days=14):
                continue
        except:
            continue

        acc_no_nodash = acc_no.replace("-", "")
        txt_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_no_nodash}/form4.txt"

        try:
            txt_res = requests.get(txt_url, headers=headers)
            if txt_res.status_code != 200:
                print(f"⚠️ Could not fetch Form 4 for {ticker}: {txt_url}")
                continue

            trades = parse_form4_txt(txt_res.text)

            if not trades:
                print(f"⚠️ No trades found in {acc_no} for {ticker}")
                continue

            for trade in trades:
                print(f"📄 {ticker} | {trade['owner']} | {trade['trade_type']} | {trade['amount']} @ ${trade['price']} → ${trade['dollar_value']:.2f}")

                if trade["dollar_value"] >= 1:  # Lowered threshold for debugging
                    alerts.append({
                        "ticker": ticker,
                        **trade
                    })

        except Exception as e:
            print(f"❌ Error parsing trade for {ticker}: {e}")

# Save alerts to insider_flow.json
with open("insider_flow.json", "w") as f:
    json.dump(alerts, f, indent=2)

print(f"✅ insider_flow.json saved with {len(alerts)} alerts.")