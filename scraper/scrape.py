import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

HOME_URL = "https://maps.westsuffolk.gov.uk/"
AAE_URL = "https://maps.westsuffolk.gov.uk/?action=SetAddress&UniqueId=10010691280"

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

        # Reliable selector for the bin panel
        try:
            await page.wait_for_selector("div.atPanelData", timeout=15000)
        except Exception:
            # Fallback: AAE didn't load or selector changed
            Path("docs/aae_failed.html").write_text(await page.content(), encoding="utf-8")
            Path("docs/next.json").write_text(
                '{"error": "AAE did not load"}',
                encoding="utf-8"
            )
            await browser.close()
            return

        # Save the AAE HTML for parsing in Step 3
        Path("docs/aae_raw.html").write_text(await page.content(), encoding="utf-8")

        # Placeholder until parsing logic is added
        Path("docs/next.json").write_text(
            '{"status": "AAE loaded"}',
            encoding="utf-8"
        )

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
