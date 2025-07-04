from send_telegram import send_alert
from parser import parse_urls

def main():
    urls = parse_urls()
    if urls:
        for url in urls:
            message = f"🔔 New Form 4 Alert:\n{url}"
            send_alert(message)
    else:
        print("✅ No fresh Form 4s found.")

if __name__ == "__main__":
    main()