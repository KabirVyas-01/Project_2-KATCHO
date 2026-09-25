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
        
        # -> Fill 'Player Cara' into the display name field and click the '🎮 Host New Room' button to create a room.
        # e.g. Maverick, Sherlock text field
        elem = page.get_by_role("textbox", name="YOUR DISPLAY NAME")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Player Cara")
        
        # -> Fill 'Player Cara' into the display name field and click the '🎮 Host New Room' button to create a room.
        # 🎮 Host New Room button
        elem = page.get_by_role("button", name="🎮 Host New Room")
        await elem.click(timeout=10000)
        
        # -> Enter 'moonlight' into the 'ENTER SECRET WORD...' field and click the 'Lock Word' button to lock the secret word.
        # ENTER SECRET WORD... text field
        elem = page.get_by_role("textbox", name="ENTER SECRET WORD...")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("moonlight")
        
        # -> Enter 'moonlight' into the 'ENTER SECRET WORD...' field and click the 'Lock Word' button to lock the secret word.
        # Lock Word 🔐 button
        elem = page.get_by_role("button", name="Lock Word 🔐")
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> Locking the secret word should show the word as locked and display a lock confirmation.
        # Assert-outcome: failed
        # Assert: Expected the 'Lock Word 🔐' button to be hidden after locking to indicate the word was locked.
        await expect(page.locator("xpath=/html/body/div[1]/main/section[2]/div[1]/div[1]/div[2]/div[1]/div[1]/button").nth(0)).not_to_be_visible(timeout=15000), "Expected the 'Lock Word \ud83d\udd10' button to be hidden after locking to indicate the word was locked."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    