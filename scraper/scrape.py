import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BAE_URL = "https://maps.westsuffolk.gov.uk/"
POSTCODE = "CB9 9SG"  # Set your postcode here
ADDRESS_TEXT = "25 Sperling Drive, Haverhill, CB9 9SG"  # Exact text match

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Step 1: Load the BAE page
        await page.goto(BAE_URL, timeout=60000)

        # ALWAYS write debug.html immediately so we can see what GitHub Actions receives
        html = await page.content()
        Path("docs/debug.html").write_text(html, encoding="utf-8")

        # Step 2: Enter postcode into the confirmed input element
        await page.fill("#atTextSearch", POSTCODE)

        # Step 3: Wait for the address list to appear
        await page.wait_for_selector("li[data-address]", timeout=30000)

        # Step 4: Select the correct address by matching its visible text
        await page.click(f"li[data-address] >> text={ADDRESS_TEXT}")

        # Step 5: Click the confirmed Find button
        await page.click("input.atSearchBtn")

        # Step 6: Wait for the AAE bin results to load
        await page.wait_for_selector("#atWasteCollection", timeout=30000)

        # Step 7: Extract the bin data from the AAE page
        aae_html = await page.content()
        Path("docs/debug.html").write_text(aae_html, encoding="utf-8")

        # Step 8: Save next.json (placeholder until we parse the real AAE structure)
        Path("docs/next.json").write_text(
            '{"status": "AAE page loaded — parsing not yet implemented"}',
            encoding="utf-8"
        )

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
