import json
import datetime
import requests

UPRN = "10010691280"

# ⚠️ You’ll probably need to tweak this once we see the real API URL.
API_URL = f"https://maps.westsuffolk.gov.uk/MyHouseService.svc/GetPropertyInfo?uprn={UPRN}"

OUTPUT_FILE = "next.json"


def fetch_property_info():
    resp = requests.get(API_URL, timeout=10)
    resp.raise_for_status()
    return resp.json()


def pick_next_and_following(collections):
    """
    collections: list of dicts with at least:
      - 'date' (ISO or UK date string)
      - 'types' (list of strings, e.g. ["Green", "Food"])
    This is the structure we’ll align to once we see the real API.
    """
    # Sort by date ascending
    def parse_date(d):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.datetime.strptime(d, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Unrecognised date format: {d}")

    sorted_cols = sorted(collections, key=lambda c: parse_date(c["date"]))

    next_col = sorted_cols[0]
    following_col = sorted_cols[1] if len(sorted_cols) > 1 else None

    result = {
        "next": {
            "date": parse_date(next_col["date"]).isoformat(),
            "types": next_col.get("types", []),
        }
    }

    if following_col:
        result["following"] = {
            "date": parse_date(following_col["date"]).isoformat(),
            "types": following_col.get("types", []),
        }

    return result


def main():
    data = fetch_property_info()

    # --- TEMP: dump full JSON so we can see the real structure ---
    with open("raw_westsuffolk.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # ⚠️ The next bit is an assumption until we see raw_westsuffolk.json.
    # Adjust `collections_source` once we know where the bin data lives.
    #
    # Example target structure (what we want to end up with):
    # collections = [
    #   {"date": "2024-01-12", "types": ["Green", "Food"]},
    #   {"date": "2024-01-19", "types": ["Black", "Food"]},
    # ]
    #
    # For now, just fail loudly so we don’t silently write bad JSON.
    raise RuntimeError(
        "Inspect raw_westsuffolk.json to locate bin collection data, "
        "then build the `collections` list and call pick_next_and_following(collections)."
    )

    # Once mapped, you’ll do something like:
    # collections = build_collections_from_api(data)
    # result = pick_next_and_following(collections)
    # with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    #     json.dump(result, f, indent=2)


if __name__ == "__main__":
    main()
