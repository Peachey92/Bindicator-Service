import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

HOME_URL = "https://maps.westsuffolk.gov.uk/"
AAE_URL = "https://maps.westsuffolk.gov.uk/?action=SetAddress&UniqueId=10010691280"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = await browser.new_context()
        page = await context.new_page()

        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))

        print("Loading homepage to establish session…")
        await page.goto(HOME_URL, timeout=60000)

        # Save initial debug
        Path("docs/console.txt").write_text("\n".join(console_messages), encoding="utf-8")
        Path("docs/debug.html").write_text(await page.content(), encoding="utf-8")
        print("Homepage loaded")

        # Step 2: Navigate to AAE using the established session
        print("Navigating to AAE…")
        await page.goto(AAE_URL, timeout=60000)

        # Step 3: Wait for AAE content
        await page.wait_for_selector("#atWasteCollection", timeout=60000)
        print("Reached AAE")

        # Save AAE debug
        Path("docs/aae_debug.html").write_text(await page.content(), encoding="utf-8")

        Path("docs/next.json").write_text(
            '{"status": "AAE page loaded — parsing not yet implemented"}',
            encoding="utf-8"
        )

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
