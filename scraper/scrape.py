import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

HOME_URL = "https://maps.westsuffolk.gov.uk/"
AAE_URL = "https://maps.westsuffolk.gov.uk/?action=SetAddress&UniqueId=10010691280"

async def dump(page, filename):
    Path(f"docs/{filename}").write_text(await page.content(), encoding="utf-8")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,   # IMPORTANT: headful mode
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
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
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Sec-Ch-Ua": '"Chromium";v="118", "Google Chrome";v="118", ";Not A Brand";v="99"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": "Windows"
            }
        )

        page = await context.new_page()

        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))

        print("STEP 1: Loading homepage…")
        await page.goto(HOME_URL, wait_until="domcontentloaded", timeout=60000)
        await dump(page, "debug_step1_home.html")

        print("STEP 2: Before navigating to AAE…")
        await dump(page, "debug_step2_before_aae.html")

        print("STEP 3: Navigating to AAE…")
        await page.goto(AAE_URL, wait_until="domcontentloaded", timeout=60000)
        await dump(page, "debug_step3_after_aae_goto.html")

        print("STEP 4: Before waiting for selector…")
        await dump(page, "debug_step4_before_selector.html")

        try:
            await page.wait_for_selector("#atWasteCollection", timeout=15000)
            print("AAE selector found")
        except Exception as e:
            print("Selector wait failed:", e)

        print("STEP 5: After selector wait…")
        await dump(page, "debug_step5_after_selector.html")

        Path("docs/next.json").write_text(
            '{"status": "debug complete — inspect debug_step*.html files"}',
            encoding="utf-8"
        )

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
