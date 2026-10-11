import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://mapstest.westsuffolk.gov.uk/MyWestSuffolk.aspx"
OUTPUT_PATH = "docs/next.json"

def fetch_page():
    r = requests.get(URL, timeout=20)
    r.raise_for_status()
    return r.text

def parse_bins(html):
    soup = BeautifulSoup(html, "html.parser")

    panel = soup.find("div", {"aria-label": "Waste and recycling"})
    if not panel:
        return {"error": "Bin panel not found"}

    data = panel.find("div", class_="atPanelData")
    if not data:
        return {"error": "Bin data not found"}

    lines = [line.strip() for line in data.stripped_strings]

    bins = {}
    for line in lines:
        if ":" in line:
            name, date = line.split(":", 1)
            bins[name.strip()] = date.strip()

    return bins

def main():
    html = fetch_page()

with open("docs/debug.html", "w", encoding="utf-8") as f:
    f.write(html)
    bins = parse_bins(html)

    os.makedirs("docs", exist_ok=True)

    with open(OUTPUT_PATH, "w") as f:
        json.dump(bins, f, indent=2)

if __name__ == "__main__":
    main()
