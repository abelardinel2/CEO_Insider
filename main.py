import os
import json
import fetcher
import send_telegram
from datetime import datetime  # make sure this is here!

def main():
    try:
        # 1️⃣ Fetch updated insider flow for all CIKs
        fetcher.fetch_and_update_insider_flow()

        # 2️⃣ Loop through each ticker JSON and send alert(s)
        for file in os.listdir():
            if file.endswith("_insider.json"):
                ticker = file.split("_")[0]
                with open(file, "r") as f:
                    try:
                        data = json.load(f)
                        # Optional: put your custom parse logic here!
                        # Example: dummy fake alert to test:
                        send_telegram.send_alert(
                            ticker,
                            "Insider",
                            "Buy",
                            1000,
                            "🤑💰 Insider Accumulation",
                            f"https://www.sec.gov/edgar/browse/?CIK={ticker}"
                        )
                    except json.JSONDecodeError:
                        print(f"❌ Skipped {file}: Invalid JSON.")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        with open("output.log", "a") as f:
            f.write(f"{datetime.now()} - Unexpected error: {e}\n")

if __name__ == "__main__":
    main()