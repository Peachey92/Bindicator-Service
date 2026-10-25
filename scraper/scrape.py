import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import re
from datetime import datetime, date
import json

HOME_URL = "https://maps.westsuffolk.gov.uk/"
AAE_URL = "https://maps.westsuffolk.gov.uk/?action=SetAddress&UniqueId=10010691280"


def parse_bin_panel(html: str):
    """
    Extracts bin types and dates from the 'Your next bin collection days are' panel.
    Returns a dict: { "Food": date, "Black": date, ... }
    """

    # Find the section that contains 'Your next bin collection days are'
    anchor_match = re.search(
        r'Your next bin collection days are:(.*?<div class="atPanelData">(.*?)</div>)',
        html,
        re.S
    )

    if not anchor_match:
        return None

    panel_html = anchor_match.group(2)

    # Extract entries like:
    # <strong>Food Bins:</strong> Friday 30th October
    entries = re.findall(
        r'<strong>\s*(.*?)\s*Bins:\s*</strong>\s*([^<]+)',
        panel_html,
        re.S
    )

    if not entries:
        return None

    results = {}
    for raw_type, raw_date in entries:
        # Clean bin type (collapse whitespace)
        bin_type = " ".join(raw_type.split())

        # Clean date string (remove ordinal suffixes and extra spaces)
        cleaned_date = (
            raw_date.replace("st", "")
                    .replace("nd", "")
                    .replace("rd", "")
                    .replace("th", "")
        ).strip()

        # Convert "Friday 30 October" → datetime.date
        try:
            parsed = datetime.strptime(cleaned_date, "%A %d %B").date()
        except ValueError:
            return None

        # Year is missing → assume current or next year
        today = date.today()
        parsed = parsed.replace(year=today.year)
        if parsed < today:
            parsed = parsed.replace(year=today.year + 1)

        results[bin_type] = parsed

    return results


def compute_next_bin(bin_dates: dict):
    """
    Returns all bins collected on the next upcoming date.
    This supports:
    - Colour + Food (normal)
    - Food-only (future)
    - Colour-only (unlikely)
    """

    today = date.today()

    # Find earliest date
    earliest_date = min(bin_dates.values())

    # Collect all bins with that date
    bins = [bin_type for bin_type, d in bin_dates.items() if d == earliest_date]

    return {
        "type": bins,
        "date": earliest_date.isoformat(),
        "days_until": (earliest_date - today).days
    }


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--window-size=1920,1080"
            ]
        )

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/118.0.5993.90 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-GB",
            extra_http_headers={
                "Referer": HOME_URL,
                "Accept-Language": "en-GB,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
        )

        page = await context.new_page()

        # Load homepage to establish session cookies
        await page.goto(HOME_URL, wait_until="domcontentloaded", timeout=60000)

        # Navigate directly to AAE
        await page.goto(AAE_URL, wait_until="domcontentloaded", timeout=60000)

        # Reliable selector for the bin panel container
        try:
            await page.wait_for_selector("div.atPanelContainer", timeout=15000)
        except Exception:
            Path("docs/aae_failed.html").write_text(await page.content(), encoding="utf-8")
            Path("docs/next.json").write_text(
                '{"error": "AAE did not load"}',
                encoding="utf-8"
            )
            await browser.close()
            return

        # Save the full AAE HTML
        aae_html = await page.content()
        Path("docs/aae_raw.html").write_text(aae_html, encoding="utf-8")

        # Step 3: Parse bin panel
        bin_dates = parse_bin_panel(aae_html)

        if not bin_dates:
            Path("docs/next.json").write_text(
                '{"error": "Failed to parse bin panel"}',
                encoding="utf-8"
            )
            await browser.close()
            return

        next_bin = compute_next_bin(bin_dates)

        # Write final Bindicator output
        Path("docs/next.json").write_text(
            json.dumps({"next": next_bin}, indent=2),
            encoding="utf-8"
        )

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
