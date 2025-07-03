import os
import requests
import xml.etree.ElementTree as ET
import json
from datetime import datetime, timedelta

WATCHLIST = [
    "PFE", "QUBT", "WMT", "JNJ", "COST", "PEP", "XOM", "AGI", "HL", "SILJ", "GLD",
    "IAU", "BAR", "SLV", "WPM", "AG", "B", "COIN", "JPM", "IREN", "FPI", "LAND",
    "WELL", "PSA", "O", "SMCI", "NVDA", "IONQ", "RGTI", "ARKQ", "AIQ", "TEM", "PLTR",
    "USO", "XOP", "PHO", "FIW", "XYL", "AWK", "WTRG", "UFO", "RKLB", "ASTS", "KYMR",
    "DHR", "RELIANCE"
]

def fetch_and_update_insider_flow():
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)  # ✅ 7-day range

    date_format = "%Y%m%d"

    url = (
        f"https://www.sec.gov/cgi-bin/browse-edgar?"
        f"action=getcurrent&dateb={end_date.strftime(date_format)}"
        f"&datea={start_date.strftime(date_format)}"
        f"&type=4&owner=include&output=atom"
    )

    headers = {
        "User-Agent": "OriaDawnBot (contact@oriadawn.xyz)",
        "Accept": "application/xml"
    }

    print(f"✅ Using SEC URL: {url}")

    # ... then the rest of your code ...