from send_telegram import send_alert
from parser import parse_urls

def main():
    urls = parse_urls()
    if urls:
        for url in urls:
            send_alert(f"🔔 New Form 4 Alert: {url}")
    else:
        print("✅ No new Form 4s found.")

if __name__ == "__main__":
    main()