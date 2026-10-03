import requests
from bs4 import BeautifulSoup
import json
import sys
import os

POSTCODE = "CB9 9SG"
ADDRESS = "25 Sperling Drive, Haverhill, CB9 9SG"

URL = "https://www.westsuffolk.gov.uk/WhereWeLive/bincollections/index.cfm"

def fetch_bin_data():
    # Step 1: Submit postcode
    r = requests.post(URL, data={"postcode": POSTCODE})
    soup = BeautifulSoup(r.text, "html.parser")

    # Step 2: Find the address dropdown
    select = soup.find("select", {"id": "address"})
    if not select:
        raise Exception("Could not find address dropdown")

    # Step 3: Find the correct option
    option = None
    for opt in select.find_all("option"):
        if ADDRESS.lower() in opt.text.lower():
            option = opt["value"]
            break

    if not option:
        raise Exception("Address not found in dropdown")

    # Step 4: Submit address selection
    r2 = requests.post(URL, data={"postcode": POSTCODE, "address": option})
    soup2 = BeautifulSoup(r2.text, "html.parser")

    # Step 5: Extract bin info
    rows = soup2.find_all("tr")

    next_bin = None
    next_date = None

    for row in rows:
        cols = row.find_all("td")
        if len(cols) == 2:
            bin_type = cols[0].text.strip()
            date = cols[1].text.strip()

            if "Next collection" in bin_type:
                next_bin = bin_type.replace("Next collection:", "").strip()
                next_date = date
                break

    if not next_bin:
        raise Exception("Could not find next bin collection")

    return {
        "bin": next_bin,
        "date": next_date
    }

def write_json(data):
    output_path = os.path.join("docs", "next.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    try:
        data = fetch_bin_data()
        write_json(data)
        print("Updated next.json:", data)
    except Exception as e:
        print("Error:", e)
        sys.exit(1)
