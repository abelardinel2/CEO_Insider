from fetcher import get_recent_form4_urls
from parser import parse_form4_xml
from send_telegram import send_alert

def main():
    urls = get_recent_form4_urls()
    for url in urls:
        result = parse_form4_xml(url)
        if not result:
            continue  # dead file, skip
        send_alert(result)

if __name__ == "__main__":
    main()