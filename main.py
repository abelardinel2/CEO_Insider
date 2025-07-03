import os
import json
import fetcher
import send_telegram
from datetime import datetime

def main():
    try:
        # 1️⃣ Fetch latest filings for your full watchlist:
        fetcher.fetch_watchlist_filings()

        # 2️⃣ Loop over saved *_insider.json files:
        for file in os.listdir():
            if file.endswith("_insider.json"):
                ticker = file.split("_")[0]

                with open(file, "r") as f:
                    try:
                        data = json.load(f)
                        # ✅ Example: loop recent filings for Form 4s
                        recent = data.get("filings", {}).get("recent", {})
                        forms = recent.get("form", [])
                        accession_numbers = recent.get("accessionNumber", [])
                        owners = recent.get("reportingOwner", [])
                        # Loop through and filter for Form 4
                        for i, form in enumerate(forms):
                            if form == "4":
                                acc = accession_numbers[i].replace("-", "")
                                cik = str(data.get("cik")).zfill(10)
                                link = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/index.json"
                                owner = owners[i] if i < len(owners) else "Insider"
                                send_telegram.send_alert(
                                    ticker,
                                    owner,
                                    "Buy/Sell",
                                    0,  # You can improve this with real share count if you parse it deeper!
                                    "🤑💰 Insider Activity",
                                    link
                                )

                    except json.JSONDecodeError:
                        print(f"❌ {file}: Invalid JSON")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        with open("output.log", "a") as f:
            f.write(f"{datetime.now()} - Unexpected error: {e}\n")

if __name__ == "__main__":
    main()