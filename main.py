import json
import time
from datetime import datetime, timedelta
from fetcher import fetch_recent_form4_urls
from parse_form4_txt import extract_form4_data
from send_alert import send_alert

# Load your CIK watchlist
with open("cik_watchlist.json", "r") as file:
    cik_data = json.load(file)

# Time filter: past 7 days
cutoff_date = datetime.utcnow() - timedelta(days=7)

for ticker, cik in cik_data.items():
    print(f"🔍 Checking {ticker} (CIK {cik})")

    try:
        # Step 1: Get recent filings
        form4_urls = fetch_recent_form4_urls(cik, days_back=7)

        for url in form4_urls:
            # Step 2: Parse Form 4
            form_data = extract_form4_data(url)

            if not form_data:
                continue

            for txn in form_data["transactions"]:
                # Extract fields
                code = txn.get("code")
                date_str = txn.get("date")
                shares = txn.get("shares", 0)
                owner = txn.get("owner")

                # Parse and check date
                try:
                    txn_date = datetime.strptime(date_str, "%Y-%m-%d")
                except Exception:
                    continue

                if txn_date < cutoff_date:
                    continue

                # Filter: Code must be A (acquisition) or D (disposition)
                if code not in ["A", "D"]:
                    continue

                # Filter: Shares must exceed $95K estimated value (we assume 1 share ≈ $1 for simplicity or customize)
                if shares < 95000:
                    continue

                # Determine bias
                bias = "Bullish ✅" if code == "A" else "Bearish ❌"

                # Send Telegram alert
                send_alert(
                    ticker=ticker,
                    owner=owner,
                    trade_type="Buy" if code == "A" else "Sell",
                    amount=shares,
                    bias=bias,
                    link=url
                )

                time.sleep(1)  # avoid hitting API too fast

    except Exception as e:
        print(f"❌ Error checking {ticker}: {e}")