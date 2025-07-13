import feedparser
import re

FORM4_FEED_URL = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=4&owner=only&count=100&output=atom"

def extract_cik_from_url(url):
    match = re.search(r'CIK=(\d+)', url)
    return match.group(1) if match else None

def fetch_recent_form4_entries():
    feed = feedparser.parse(FORM4_FEED_URL)
    entries = []

    for entry in feed.entries:
        if "form type" in entry.title.lower() and "4" in entry.title:
            cik = extract_cik_from_url(entry.link)
            if cik:
                entries.append({
                    "cik": cik,
                    "url": entry.link
                })

    return entries
