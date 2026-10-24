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
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = await browser.new_context()
        page = await context.new_page()

        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))

        print("STEP 1: Loading homepage…")
        await page.goto(HOME_URL, wait_until="domcontentloaded", timeout=60000)
        await dump(page, "debug_step1_home.html")

        Path("docs/console.txt").write_text("\n".join(console_messages), encoding="utf-8")
        print("Homepage loaded")

        print("STEP 2: Before navigating to AAE…")
        await dump(page, "debug_step2_before_aae.html")

        print("STEP 3: Navigating to AAE…")
        await page.goto(AAE_URL, wait_until="domcontentloaded", timeout=60000)
        await dump(page, "debug_step3_after_aae_goto.html")

        print("STEP 4: Before waiting for AAE selector…")
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
