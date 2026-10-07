import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# This is the page that shows your bin info AFTER selecting your address.
# It does NOT change URL, so we just request it directly.
PAGE_URL = "https://maps.westsuffolk.gov.uk/MyWestSuffolk.aspx"

OUTPUT_FILE = "next.json"


def fetch_html():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.9",
        "Referer": "https://maps.westsuffolk.gov.uk/",
        "Connection": "keep-alive",
    }

    resp = requests.get(PAGE_URL, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.text


def parse_bin_section(html):
    soup = BeautifulSoup(html, "html.parser")

    # Find the bin section container
    panel = soup.find("div", class_="atPanelData")
    if not panel:
        raise RuntimeError("Could not find .atPanelData in page HTML")

    bins = {}

    # Split the HTML by <br/> tags
    for line in panel.decode_contents().split("<br"):
        line_soup = BeautifulSoup(line, "html.parser")
        strong = line_soup.find("strong")
        if strong:
            bin_type = strong.text.replace(":", "").strip()
            # The date is the text node immediately after <strong>
            date_text = strong.next_sibling.strip()
            bins[bin_type] = date_text

    return bins


def convert_to_bindicator_format(bins):
    """
    Convert the raw bin dict into the Bindicator JSON format:
    {
      "next": { "date": "...", "types": [...] },
      "following": { ... }
    }
    """

    # Convert each date into a real datetime so we can sort them
    parsed = []
    for bin_type, date_str in bins.items():
        try:
            # Example: "Friday 9th October"
            date_obj = datetime.strptime(date_str, "%A %dth %B")
        except ValueError:
            # Try without "th", "rd", "st"
            cleaned = (
                date_str.replace("th", "")
                .replace("rd", "")
                .replace("st", "")
                .replace("nd", "")
            )
            date_obj = datetime.strptime(cleaned, "%A %d %B")

        parsed.append({
            "date": date_obj,
            "type": bin_type
        })

    # Sort by date
    parsed.sort(key=lambda x: x["date"])

    # Build Bindicator JSON
    next_date = parsed[0]["date"].strftime("%Y-%m-%d")
    next_types = [parsed[0]["type"]]

    following_date = parsed[1]["date"].strftime("%Y-%m-%d") if len(parsed) > 1 else None
    following_types = [parsed[1]["type"]] if len(parsed) > 1 else []

    result = {
        "next": {
            "date": next_date,
            "types": next_types
        }
    }

    if following_date:
        result["following"] = {
            "date": following_date,
            "types": following_types
        }

    return result


def main():
    html = fetch_html()
    bins = parse_bin_section(html)
    result = convert_to_bindicator_format(bins)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("Updated next.json")


if __name__ == "__main__":
    main()
