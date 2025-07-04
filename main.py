from fetcher import get_recent_form4_urls
from parser import parse_form4_xml
from send_telegram import send_to_telegram

def main():
    urls = get_recent_form4_urls()
    for url in urls:
        try:
            result = parse_form4_xml(url)

            if result["net_shares"] != 0:
                if result["net_shares"] > 0:
                    bias = "🟢 Insider Net Accumulation"
                else:
                    bias = "🔴 Insider Net Disposal"

                msg = (
                    f"{bias}\n"
                    f"Date: {result['date']}\n"
                    f"Net Shares: {result['net_shares']:.0f}\n"
                    f"Net Value: ${result['net_value']:.2f}\n"
                    f"[View Filing]({url})"
                )

                send_to_telegram(msg)

        except Exception as e:
            print(f"❌ Error on {url}: {e}")

if __name__ == "__main__":
    main()