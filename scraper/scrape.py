import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BAE_URL = "https://maps.westsuffolk.gov.uk/?action=SetAddress&UniqueId=10010691280"

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

        print("Loading AAE directly…")
        await page.goto(BAE_URL, timeout=60000)

        # Save console
        Path("docs/console.txt").write_text("\n".join(console_messages), encoding="utf-8")

        # Save AAE HTML + screenshot
        aae_html = await page.content()
        Path("docs/aae_debug.html").write_text(aae_html, encoding="utf-8")
        await page.screenshot(path="docs/aae.png")
        print("Reached AAE")

        # Placeholder next.json
        Path("docs/next.json").write_text(
            '{"status": "AAE page loaded — parsing not yet implemented"}',
            encoding="utf-8"
        )

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
