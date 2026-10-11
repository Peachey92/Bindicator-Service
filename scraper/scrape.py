import requests
import json
import os

# CONFIG — you will fill these in
UPRN = "10010691280"

# West Suffolk’s GetData endpoint
BASE_URL = "https://mapstest.westsuffolk.gov.uk/getdata.aspx"

# The group name for waste/recycling varies by council.
# Common values: "Waste Collection", "Refuse Collection", "Recycling Collection"
GROUP = "Waste Collection"

OUTPUT_JSON = "docs/next.json"
DEBUG_HTML = "docs/debug.html"


def fetch_localinfo(uprn, group):
    """
    Calls Astun's GetData LocalInfo API directly.
    This bypasses the entire MyWestSuffolk.aspx UI.
    """
    params = {
        "RequestType": "LocalInfo",
        "ms": "mapsources/MyHouse",   # typical profile name; councils vary
        "format": "JSON",
        "uid": uprn,
        "group": group
    }

    r = requests.get(BASE_URL, params=params, timeout=20)
    r.raise_for_status()
    return r.text


def parse_bins(json_text):
    """
    Extracts bin collection dates from the LocalInfo JSON.
    The exact structure varies by council, but most follow:
    {
      "Items": [
        {"Name": "Refuse", "NextCollection": "2024-10-12"},
        {"Name": "Recycling", "NextCollection": "2024-10-19"}
      ]
    }
    """
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON returned from GetData"}

    items = data.get("Items")
    if not items:
        return {"error": "No bin items found in LocalInfo response"}

    bins = {}
    for item in items:
        name = item.get("Name")
        date = item.get("NextCollection") or item.get("CollectionDate")
        if name and date:
            bins[name] = date

    return bins


def main():
    os.makedirs("docs", exist_ok=True)

    # Fetch raw JSON from GetData API
    raw = fetch_localinfo(UPRN, GROUP)

    # Save raw response for debugging
    with open(DEBUG_HTML, "w", encoding="utf-8") as f:
        f.write(raw)

    # Parse bin data
    bins = parse_bins(raw)

    # Save parsed bin data
    with open(OUTPUT_JSON, "w") as f:
        json.dump(bins, f, indent=2)


if __name__ == "__main__":
    main()
