import json
from fetch_api import fetch_recent_form4
from send_alert import send_alert

with open("cik_watchlist.json") as f:
    watchlist = json.load(f)

for ticker, info in watchlist.items():
    cik = info["cik"]
    filings = fetch_recent_form4(cik)
    for filing in filings:
        alert_msg = f"📢 Insider Alert: {ticker}\n👤 Insider: {filing['owner']}\nType: {filing['type']}\nAmount: {filing['amount']} shares\nBias: {filing['bias']}\nLink: {filing['link']}"
        send_alert(alert_msg)