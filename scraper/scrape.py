import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

BAE_URL = "https://maps.westsuffolk.gov.uk/"
POSTCODE = "CB9 9SG"          # change as needed
ADDRESS_INDEX = 0             # which address to pick from the list

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Step 1: Reach BAE
        await page.goto(BAE_URL, timeout=60000)

        # Step 2: Enter postcode exactly like a human
        await page.fill("#txtSearch", POSTCODE)
        await page.click("#btnSearch")

        # Wait for the address list to appear
        await page.wait_for_selector("#lstResults option", timeout=60000)

        # Select the first matching address
        options = await page.query_selector_all("#lstResults option")
        await options[ADDRESS_INDEX].click()

        # Click "My House" tab (this triggers the AAE content)
        await page.click("#btnMyHouse")

        # Step 3: Wait for bin data to load
        await page.wait_for_selector("#divBinCollection", timeout=60000)

        # Capture full HTML for debugging
        html = await page.content()
        Path("docs/debug.html").write_text(html, encoding="utf-8")

        # Extract bin data
        bin_div = await page.query_selector("#divBinCollection")
        bin_text = await bin_div.inner_text()

        # Step 4: Save in hardware-friendly JSON
        result = {
            "raw": bin_text
        }
        Path("docs/next.json").write_text(json.dumps(result, indent=2))

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
