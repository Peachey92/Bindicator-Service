import requests
from bs4 import BeautifulSoup
import json

BASE = "https://mapstest.westsuffolk.gov.uk"

def search_postcode(postcode):
    url = f"{BASE}/getdata.aspx"
    params = {
        "service": "LocationSearch",
        "RequestType": "LocationSearch",
        "location": postcode,
        "pagesize": 20,
        "startnum": 1,
        "gettotals": "false",
        "mapsource": "mapsources/MyHouse",
        "type": "jsonp"
    }
    r = requests.get(url, params=params)
    text = r.text

    # Strip JSONP wrapper
    json_start = text.find("(") + 1
    json_end = text.rfind(")")
    data = json.loads(text[json_start:json_end])

    # Pick first matching address
    result = data["results"][0]
    return result["uprn"], result["address"]

def fetch_aae_page(uprn):
    url = f"{BASE}/MyWestSuffolk.aspx"
    params = {
        "uprn": uprn,
        "tab": "MyHouse"
    }
    r = requests.get(url, params=params)
    return r.text

def parse_bins(html):
    soup = BeautifulSoup(html, "html.parser")

    panel = soup.find("div", {"aria-label": "Waste and recycling"})
    if not panel:
        return None

    data = panel.find("div", class_="atPanelData")
    lines = [line.strip() for line in data.stripped_strings]

    bins = {}
    for line in lines:
        if ":" in line:
            name, date = line.split(":", 1)
            bins[name.strip()] = date.strip()

    return bins

def get_bin_schedule(postcode):
    uprn, address = search_postcode(postcode)
    html = fetch_aae_page(uprn)
    bins = parse_bins(html)
    return {
        "address": address,
        "uprn": uprn,
        "bins": bins
    }

print(get_bin_schedule("CB9 9SG"))
