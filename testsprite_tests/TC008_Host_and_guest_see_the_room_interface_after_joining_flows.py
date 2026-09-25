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
        
        # -> Enter 'FlowPlayer' into the display name field, then click the '🎮 Host New Room' button to host a new room.
        # e.g. Maverick, Sherlock text field
        elem = page.get_by_role("textbox", name="YOUR DISPLAY NAME")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("FlowPlayer")
        
        # -> Enter 'FlowPlayer' into the display name field, then click the '🎮 Host New Room' button to host a new room.
        # 🎮 Host New Room button
        elem = page.get_by_role("button", name="🎮 Host New Room")
        await elem.click(timeout=10000)
        
        # -> In a new tab, fill 'JoinPlayer' into the Display Name field, enter room code 'FRRH' into the room code field, and click the '🚀 Join Room' button to join the existing room.
        # Open URL in new tab
        page = await context.new_page()
        await page.goto("http://localhost:8000/")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> In the second tab, fill the display name with 'JoinPlayer', enter room code 'FRRH', and click the '🚀 Join Room' button to join the room.
        # Switch to tab DA24
        page = context.pages[-1]  # switch to most recently active tab
        
        # -> In the second tab, fill the display name with 'JoinPlayer', enter room code 'FRRH', and click the '🚀 Join Room' button to join the room.
        # e.g. Maverick, Sherlock text field
        elem = page.get_by_role("textbox", name="YOUR DISPLAY NAME")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("JoinPlayer")
        
        # -> In the second tab, fill the display name with 'JoinPlayer', enter room code 'FRRH', and click the '🚀 Join Room' button to join the room.
        # CODE text field
        elem = page.get_by_role("textbox", name="CODE")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("FRRH")
        
        # -> In the second tab, fill the display name with 'JoinPlayer', enter room code 'FRRH', and click the '🚀 Join Room' button to join the room.
        # 🚀 Join Room button
        elem = page.get_by_role("button", name="🚀 Join Room")
        await elem.click(timeout=10000)
        
        # -> Switch to the second tab opened for joining (tab title: 'KATCHO — Multiplayer Social De') so the join inputs can be filled.
        # Switch to tab DA24
        page = context.pages[-1]  # switch to most recently active tab
        
        # -> Fill the 'YOUR DISPLAY NAME' field with 'JoinPlayer', enter room code 'FRRH' into the room code field, and click the '🚀 Join Room' button.
        # e.g. Maverick, Sherlock text field
        elem = page.get_by_role("textbox", name="YOUR DISPLAY NAME")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("JoinPlayer")
        
        # -> Fill the 'YOUR DISPLAY NAME' field with 'JoinPlayer', enter room code 'FRRH' into the room code field, and click the '🚀 Join Room' button.
        # 🚀 Join Room button
        elem = page.get_by_role("button", name="🚀 Join Room")
        await elem.click(timeout=10000)
        
        # -> Enter the room code 'FRRH' into the room code field and click the '🚀 Join Room' button to join the existing room.
        # CODE text field
        elem = page.get_by_role("textbox", name="CODE")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("FRRH")
        
        # -> Enter the room code 'FRRH' into the room code field and click the '🚀 Join Room' button to join the existing room.
        # 🚀 Join Room button
        elem = page.get_by_role("button", name="🚀 Join Room")
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> Room lobby UI is displayed with the '✨ Begin Reveal Sequence' control visible.
        await page.get_by_role("button", name="✨ Begin Reveal Sequence").nth(0).scroll_into_view_if_needed()
        # Assert-outcome: passed
        # Assert: The lobby's Begin Reveal Sequence button is visible.
        await expect(page.get_by_role("button", name="✨ Begin Reveal Sequence").nth(0)).to_be_visible(timeout=15000), "The lobby's Begin Reveal Sequence button is visible."
        
        # --> Live player roster is visible and contains the joined player 'JoinPlayer (You)'.
        # Assert-outcome: passed
        # Assert: The roster contains the joined player 'JoinPlayer (You)'.
        await expect(page.locator("#playerRosterGrid").nth(0)).to_contain_text("JoinPlayer (You)", timeout=15000), "The roster contains the joined player 'JoinPlayer (You)'."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    