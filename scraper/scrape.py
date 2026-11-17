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
    Extracts bin types and dates from the
    'Your next bin collection days are' panel.

    Returns:
    {
        "Food": date(...),
        "Black": date(...),
        ...
    }
    """

    anchor_match = re.search(
        r'Your next bin collection days are:(.*?<div class="atPanelData">(.*?)</div>)',
        html,
        re.S
    )

    if not anchor_match:
        return None

    panel_html = anchor_match.group(2)

    entries = re.findall(
        r'<strong>\s*(.*?)\s*Bins:\s*</strong>\s*([^<]+)',
        panel_html,
        re.S
    )

    if not entries:
        return None

    results = {}

    for raw_type, raw_date in entries:

        bin_type = " ".join(raw_type.split())

        cleaned_date = (
            raw_date.replace("st", "")
                    .replace("nd", "")
                    .replace("rd", "")
                    .replace("th", "")
        ).strip()

        try:
            parsed = datetime.strptime(
                cleaned_date,
                "%A %d %B"
            ).date()

        except ValueError:
            return None

        today = date.today()

        parsed = parsed.replace(year=today.year)

        if parsed < today:
            parsed = parsed.replace(year=today.year + 1)

        results[bin_type] = parsed

    return results


def compute_next_bin(bin_dates: dict):
    """
    Returns all bins collected on the next upcoming date.
    Supports:

    - Colour + Food
    - Food only
    - Colour only
    """

    today = date.today()

    earliest_date = min(bin_dates.values())

    bins = [
        bin_type
        for bin_type, d in bin_dates.items()
        if d == earliest_date
    ]

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
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/118.0.5993.90 Safari/537.36"
            ),
            viewport={
                "width": 1920,
                "height": 1080
            },
            locale="en-GB",
            extra_http_headers={
                "Referer": HOME_URL,
                "Accept-Language": "en-GB,en;q=0.9",
                "Accept": (
                    "text/html,"
                    "application/xhtml+xml,"
                    "application/xml;q=0.9,*/*;q=0.8"
                )
            }
        )

        page = await context.new_page()

        # Establish session cookies

        await page.goto(
            HOME_URL,
            wait_until="domcontentloaded",
            timeout=60000
        )

        # Navigate directly to address page

        await page.goto(
            AAE_URL,
            wait_until="domcontentloaded",
            timeout=60000
        )

        try:

            await page.wait_for_selector(
                "div.atPanelContainer",
                timeout=15000
            )

        except Exception:

            Path("docs/aae_failed.html").write_text(
                await page.content(),
                encoding="utf-8"
            )

            Path("docs/next.json").write_text(
                '{"error": "AAE did not load"}',
                encoding="utf-8"
            )

            await browser.close()
            return

        # Read page HTML into memory

        aae_html = await page.content()

        # Extract collection information

        bin_dates = parse_bin_panel(aae_html)

        if not bin_dates:

            Path("docs/next.json").write_text(
                '{"error": "Failed to parse bin panel"}',
                encoding="utf-8"
            )

            await browser.close()
            return

        # Existing Bindicator output

        next_bin = compute_next_bin(bin_dates)

        Path("docs/next.json").write_text(
            json.dumps(
                {"next": next_bin},
                indent=2
            ),
            encoding="utf-8"
        )

        # New website-friendly schedule output

        schedule = {
            name: value.isoformat()
            for name, value in bin_dates.items()
        }

        Path("docs/schedule.json").write_text(
            json.dumps(
                schedule,
                indent=2
            ),
            encoding="utf-8"
        )

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
