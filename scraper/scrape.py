import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BAE_URL = "https://maps.westsuffolk.gov.uk/"
POSTCODE = "25 CB9 9SG"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = await browser.new_context()
        page = await context.new_page()

        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))

        print("Loading BAE…")
        await page.goto(BAE_URL, timeout=60000)

        Path("docs/console.txt").write_text("\n".join(console_messages), encoding="utf-8")
        Path("docs/debug.html").write_text(await page.content(), encoding="utf-8")
        await page.screenshot(path="docs/bae.png")
        print("Reached BAE")

        # Step 1: Enter postcode
        await page.fill("#atTextSearch", POSTCODE)
        print("Filled postcode")

        # Step 2: TAB into dropdown
        await page.press("#atTextSearch", "Tab")
        print("Pressed Tab")

        # Step 3: ENTER to select first dropdown item
        await page.press("#atTextSearch", "Enter")
        print("Pressed Enter to select dropdown item")

        # Step 4: Wait for AAE page
        await page.wait_for_selector("#atWasteCollection", timeout=30000)
        print("Reached AAE")

        # Step 5: Dump AAE debug
        Path("docs/aae_debug.html").write_text(await page.content(), encoding="utf-8")
        await page.screenshot(path="docs/aae.png")

        Path("docs/next.json").write_text(
            '{"status": "AAE page loaded — parsing not yet implemented"}',
            encoding="utf-8"
        )

        Path("docs/console.txt").write_text("\n".join(console_messages), encoding="utf-8")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
