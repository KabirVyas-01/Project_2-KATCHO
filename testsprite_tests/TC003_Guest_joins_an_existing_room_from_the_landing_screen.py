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
        
        # -> Fill the 'YOUR DISPLAY NAME' field with 'GuestPlayer'.
        # e.g. Maverick, Sherlock text field
        elem = page.get_by_role("textbox", name="YOUR DISPLAY NAME")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("GuestPlayer")
        
        # -> Fill the 'YOUR DISPLAY NAME' field with 'GuestPlayer'.
        # 🎮 Host New Room button
        elem = page.get_by_role("button", name="🎮 Host New Room")
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> Room interface is displayed with the secret-word controls visible.
        await page.get_by_role("button", name="✨ Begin Reveal Sequence").nth(0).scroll_into_view_if_needed()
        # Assert-outcome: passed
        # Assert: Verify the secret-word control (Begin Reveal Sequence button) is visible.
        await expect(page.get_by_role("button", name="✨ Begin Reveal Sequence").nth(0)).to_be_visible(timeout=15000), "Verify the secret-word control (Begin Reveal Sequence button) is visible."
        
        # --> Player roster is visible with at least one player entry.
        await page.get_by_text("G", exact=True).nth(0).scroll_into_view_if_needed()
        # Assert-outcome: passed
        # Assert: Verify a player roster entry is visible.
        await expect(page.get_by_text("G", exact=True).nth(0)).to_be_visible(timeout=15000), "Verify a player roster entry is visible."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    