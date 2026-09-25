import asyncio
import re
from playwright import async_api
from playwright.async_api import expect

async def run_test():
    pw = None
    browser = None
    context = None

    try:
        # Start a Playwright session in asynchronous mode
        pw = await async_api.async_playwright().start()

        # Launch a Chromium browser in headless mode with custom arguments
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--window-size=1280,720",
                "--disable-dev-shm-usage",
                "--ipc=host",
                "--single-process"
            ],
        )

        # Create a new browser context (like an incognito window)
        context = await browser.new_context()
        # Wider default timeout to match the agent's DOM-stability budget;
        # auto-waiting Playwright APIs (expect, locator.wait_for) inherit this.
        context.set_default_timeout(15000)

        # Open a new page in the browser context
        page = await context.new_page()

        # Interact with the page elements to simulate user flow
        # -> navigate
        await page.goto("http://localhost:8000")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Fill the 'YOUR DISPLAY NAME' input with 'QuickStartPlayer' and press Enter to submit the landing form.
        # e.g. Maverick, Sherlock text field
        elem = page.get_by_role("textbox", name="YOUR DISPLAY NAME")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("QuickStartPlayer")
        
        # --> Assertions to verify final state
        
        # --> The room lobby UI is displayed — the '✨ Begin Reveal Sequence' button is visible.
        # Assert-outcome: passed
        # Assert: Verify the '✨ Begin Reveal Sequence' button is visible.
        await expect(page.locator("#btnStartReveal").nth(0)).to_have_text("\u2728 Begin Reveal Sequence", timeout=15000), "Verify the '\u2728 Begin Reveal Sequence' button is visible."
        
        # --> A room badge showing a room code is visible in the header.
        await page.get_by_text("ROOM: NRPT 📋").nth(0).scroll_into_view_if_needed()
        # Assert-outcome: passed
        # Assert: The room badge (showing the room code) is visible in the header.
        await expect(page.get_by_text("ROOM: NRPT 📋").nth(0)).to_be_visible(timeout=15000), "The room badge (showing the room code) is visible in the header."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    