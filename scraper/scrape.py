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

        # Step 1: Click input and type postcode slowly
        await page.click("#atTextSearch")
        await page.keyboard.type(POSTCODE, delay=120)
        print("Typed postcode")

        # Step 1.5: Give autocomplete time to react
        await asyncio.sleep(0.5)

        # Step 2: Wait for dropdown to appear
        await page.wait_for_selector("li[data-address]", timeout=30000)
        print("Dropdown appeared")

        # Step 3: ArrowDown to highlight first item
        await page.keyboard.press("ArrowDown")
        print("Pressed ArrowDown")

        # Step 4: Enter to select it
        await page.keyboard.press("Enter")
        print("Pressed Enter to select dropdown item")

        # Step 5: Wait for AAE page
        await page.wait_for_selector("#atWasteCollection", timeout=30000)
        print("Reached AAE")

        # Step 6: Dump AAE debug
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
