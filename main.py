import json
from fetcher import get_recent_form4_urls
from parser import parse_form4
from send_telegram import send_alert  # ✅ Correct local import

def main():
    urls = get_recent_form4_urls()
    if not urls:
        print("No fresh Form 4 URLs found.")
        return

    for url in urls:
        try:
            result = parse_form4(url)
            if result:
                send_alert(result)
        except Exception as e:
            print(f"Error processing {url}: {e}")

if __name__ == "__main__":
    main()