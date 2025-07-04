from fetcher import get_recent_form4_urls
from parser import parse_form4_xml
from send_telegram import send_to_telegram

urls = get_recent_form4_urls()
print(f"✅ Found {len(urls)} fresh Form 4s to check.")

for url in urls:
    try:
        result = parse_form4_xml(url)
    except Exception as e:
        print(f"❌ Skipping broken URL: {url} — {e}")
        continue

    if not result:
        continue

    msg = ""

    if result["buys_shares"] > 0:
        msg += (
            f"🟢 *Insider Buy Alert*\n"
            f"Date: {result['date']}\n"
            f"Shares: {result['buys_shares']:.0f}\n"
            f"Value: ${result['buys_value']:.2f}\n"
        )

    if result["sells_shares"] > 0:
        msg += (
            f"🔴 *Insider Sell Alert*\n"
            f"Date: {result['date']}\n"
            f"Shares: {result['sells_shares']:.0f}\n"
            f"Value: ${result['sells_value']:.2f}\n"
        )

    if msg:
        msg += f"\n[View Filing]({url})"
        send_to_telegram(msg)
        print(f"✅ Alert sent for: {url}")