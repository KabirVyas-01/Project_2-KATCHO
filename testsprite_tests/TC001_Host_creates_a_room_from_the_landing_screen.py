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
        
        # -> Fill 'HostPlayer' into the display name field and click the '🎮 Host New Room' (Create Game) button.
        # e.g. Maverick, Sherlock text field
        elem = page.get_by_role("textbox", name="YOUR DISPLAY NAME")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("HostPlayer")
        
        # -> Fill 'HostPlayer' into the display name field and click the '🎮 Host New Room' (Create Game) button.
        # 🎮 Host New Room button
        elem = page.get_by_role("button", name="🎮 Host New Room")
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> The live room interface is open (the '✨ Begin Reveal Sequence' button is visible).
        await page.get_by_role("button", name="✨ Begin Reveal Sequence").nth(0).scroll_into_view_if_needed()
        # Assert-outcome: passed
        # Assert: The 'Begin Reveal Sequence' button is visible, indicating the room interface is displayed.
        await expect(page.get_by_role("button", name="✨ Begin Reveal Sequence").nth(0)).to_be_visible(timeout=15000), "The 'Begin Reveal Sequence' button is visible, indicating the room interface is displayed."
        
        # --> A room code is displayed in the header and the connection status reads 'Online'.
        await page.get_by_text("7EEN").nth(0).scroll_into_view_if_needed()
        # Assert-outcome: passed
        # Assert: A room code element is visible in the header.
        await expect(page.get_by_text("7EEN").nth(0)).to_be_visible(timeout=15000), "A room code element is visible in the header."
        # Assert-outcome: passed
        # Assert: The connection status text equals 'Online'.
        await expect(page.locator("#statusText").nth(0)).to_have_text("Online", timeout=15000), "The connection status text equals 'Online'."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    