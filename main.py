import os
import json
from datetime import datetime, timedelta
from fetcher import fetch_latest_form4_urls
from parse_form4_txt import parse_form4_text
from send_telegram import send_telegram_message

# Load CIKs to monitor
with open("cik_watchlist.json", "r") as f:
    cik_watchlist = json.load(f)

# Set the minimum trade value threshold
MIN_TRADE_VALUE = 95000  # $95K

# Set how many days back to check
DAYS_BACK = 7
cutoff_date = datetime.utcnow() - timedelta(days=DAYS_BACK)

# Collect alerts to save in JSON
alerts = []

for ticker, cik in cik_watchlist.items():
    print(f"🔍 Checking {ticker} (CIK {cik})")

    urls = fetch_latest_form4_urls(cik)
    if not urls:
        print(f"⚠️ No forms found for {ticker}")
        continue

    for url in urls:
        try:
            filing_date, parsed = parse_form4_text(url)
        except Exception as e:
            print(f"❌ Failed to parse {url}: {e}")
            continue

        if filing_date < cutoff_date:
            continue

        for entry in parsed:
            trade_value = entry["value"]
            transaction_type = entry["type"]

            if transaction_type in ["A", "D"] and trade_value >= MIN_TRADE_VALUE:
                alert = {
                    "ticker": ticker,
                    "cik": cik,
                    "form_url": url,
                    "filing_date": filing_date.strftime("%Y-%m-%d"),
                    "insider": entry["insider"],
                    "title": entry["title"],
                    "type": transaction_type,
                    "value": trade_value,
                    "shares": entry["shares"],
                    "bias": "💰🚢 Normal Buy" if transaction_type == "A" else "💰🚢 Normal Sell",
                }

                message = (
                    f"📢 Insider Alert: <b>{ticker}</b>\n"
                    f"🧑 Insider: <b>{alert['insider']}</b>\n"
                    f"Title: {alert['title']}\n"
                    f"Type: {alert['type']}\n"
                    f"Amount: <b>${alert['value']:,}</b>\n"
                    f"Bias: {alert['bias']}\n"
                    f"Link: {alert['form_url']}"
                )

                send_telegram_message(message)
                alerts.append(alert)

# Save alerts to file
with open("insider_flow.json", "w") as f:
    json.dump(alerts, f, indent=2)

print("✅ insider_flow.json saved.")