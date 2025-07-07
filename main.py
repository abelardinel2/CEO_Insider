
from fetcher import get_doc4_xml_url, download_xml
from parse_form4_xml import parse_form4_xml
from send_telegram import send_alert

def main():
    index_url = "https://www.sec.gov/Archives/edgar/data/78003/000122520825006305/index.json"
    xml_url = get_doc4_xml_url(index_url)
    xml_data = download_xml(xml_url)
    parsed = parse_form4_xml(xml_data)
    message = f"""
📢 Insider Alert:
Issuer: {parsed['issuer']}
Owner: {parsed['owner']}
Shares: {parsed['shares']}
Link: {xml_url}
"""
    send_alert(message)

if __name__ == "__main__":
    main()
