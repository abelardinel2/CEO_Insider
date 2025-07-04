from fetcher import get_recent_form4_urls  # your own function
from send_telegram import send_to_telegram
from parser import parse_form4_xml  # new: put parse logic in parser.py

# 1️⃣ Get your URLs
urls = get_recent_form4_urls()  # make sure this respects your cik_watchlist.json

# 2️⃣ Loop through
for url in urls:
    result = parse_form4_xml(url)
    if not result:
        continue

    msg = ""
    if result["buys_shares"] > 0:
        msg += f"🟢 *Insider Buy Alert*\nDate: {result['date']}\nShares: {result['buys_shares']:.0f}\nValue: ${result['buys_value']:.2f}\n"

    if result["sells_shares"] > 0:
        msg += f"🔴 *Insider Sell Alert*\nDate: {result['date']}\nShares: {result['sells_shares']:.0f}\nValue: ${result['sells_value']:.2f}\n"

    if msg:
        msg += f"\n[View Filing]({url})"
        send_to_telegram(msg)