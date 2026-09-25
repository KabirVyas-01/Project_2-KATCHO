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
        
        # -> Fill 'Host Alice' into the display name field and click the '🎮 Host New Room' button to create and host a new room.
        # e.g. Maverick, Sherlock text field
        elem = page.get_by_role("textbox", name="YOUR DISPLAY NAME")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Host Alice")
        
        # -> Fill 'Host Alice' into the display name field and click the '🎮 Host New Room' button to create and host a new room.
        # 🎮 Host New Room button
        elem = page.get_by_role("button", name="🎮 Host New Room")
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> Lobby is displayed (page shows the lobby UI including the secret-word entry).
        await page.get_by_role("textbox", name="ENTER SECRET WORD...").nth(0).scroll_into_view_if_needed()
        # Assert-outcome: passed
        # Assert: The lobby's secret-word input is visible.
        await expect(page.get_by_role("textbox", name="ENTER SECRET WORD...").nth(0)).to_be_visible(timeout=15000), "The lobby's secret-word input is visible."
        
        # --> Room code is visible in the header so the host can share the room link.
        await page.get_by_text("JQKP").nth(0).scroll_into_view_if_needed()
        # Assert-outcome: passed
        # Assert: The room code element in the header is visible.
        await expect(page.get_by_text("JQKP").nth(0)).to_be_visible(timeout=15000), "The room code element in the header is visible."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    