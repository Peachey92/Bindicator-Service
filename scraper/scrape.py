import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BAE_URL = "https://maps.westsuffolk.gov.uk/"
POSTCODE = "CB9 9SG"
ADDRESS_TEXT = "25 Sperling Drive, Haverhill, CB9 9SG"

async def main():
    async with async_playwright() as p:
        # ⭐ Option A: NON‑HEADLESS MODE (required for JS + cookies)
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = await browser.new_context()
        page = await context.new_page()

        print("Loading BAE…")
        await page.goto(BAE_URL, timeout=60000)

        # ⭐ Write BAE debug immediately
        bae_html = await page.content()
        Path("docs/debug.html").write_text(bae_html, encoding="utf-8")
        await page.screenshot(path="docs/bae.png")
        print("Reached BAE")

        # ⭐ Step 2: Enter postcode
        await page.fill("#atTextSearch", POSTCODE)
        print("Filled postcode")

        # ⭐ Step 3: Wait for address list
        await page.wait_for_selector("li[data-address]", timeout=30000)
        print("Address list appeared")

        # ⭐ Step 4: Select the correct address
        await page.click(f"li[data-address] >> a:has-text('{ADDRESS_TEXT}')")
        print("Clicked address")

        # ⭐ Step 5: Click Find
        await page.click("input.atSearchBtn")
        print("Clicked Find")

        # ⭐ Step 6: Wait for AAE page
        await page.wait_for_selector("#atWasteCollection", timeout=30000)
        print("Reached AAE")

        # ⭐ Step 7: Write AAE debug
        aae_html = await page.content()
        Path("docs/aae_debug.html").write_text(aae_html, encoding="utf-8")
        await page.screenshot(path="docs/aae.png")

        # ⭐ Step 8: Placeholder next.json
        Path("docs/next.json").write_text(
            '{"status": "AAE page loaded — parsing not yet implemented"}',
            encoding="utf-8"
        )

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
