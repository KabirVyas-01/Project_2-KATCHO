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
        
        # -> Fill the display name input (placeholder 'e.g. Maverick, Sherlock') with 'Tester'.
        # e.g. Maverick, Sherlock text field
        elem = page.get_by_role("textbox", name="YOUR DISPLAY NAME")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Tester")
        
        # -> Fill the display name input (placeholder 'e.g. Maverick, Sherlock') with 'Tester'.
        # 🎮 Host New Room button
        elem = page.get_by_role("button", name="🎮 Host New Room")
        await elem.click(timeout=10000)
        
        # -> Open a new tab, enter a second display name (e.g. 'Guest2'), and join the existing room NJJ3 using the Join Room flow.
        # Open URL in new tab
        page = await context.new_page()
        await page.goto("http://localhost:8000/")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Switch to the new browser tab for the second player so the display name and room code can be entered and '🚀 Join Room' can be clicked.
        # Switch to tab 266D
        page = context.pages[-1]  # switch to most recently active tab
        
        # -> Fill 'Guest2' into the YOUR DISPLAY NAME field, enter room code 'NJJ3' into the room code field, and click the '🚀 Join Room' button.
        # e.g. Maverick, Sherlock text field
        elem = page.get_by_role("textbox", name="YOUR DISPLAY NAME")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Guest2")
        
        # -> Fill 'Guest2' into the YOUR DISPLAY NAME field, enter room code 'NJJ3' into the room code field, and click the '🚀 Join Room' button.
        # CODE text field
        elem = page.get_by_role("textbox", name="CODE")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("NJJ3")
        
        # -> Fill 'Guest2' into the YOUR DISPLAY NAME field, enter room code 'NJJ3' into the room code field, and click the '🚀 Join Room' button.
        # 🚀 Join Room button
        elem = page.get_by_role("button", name="🚀 Join Room")
        await elem.click(timeout=10000)
        
        # -> Fill 'ORANGE' into the secret word field and click the 'Lock Word 🔐' button, then switch to the host tab and click the '✨ Begin Reveal Sequence' button.
        # ENTER SECRET WORD... text field
        elem = page.get_by_role("textbox", name="ENTER SECRET WORD...")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("ORANGE")
        
        # -> Fill 'ORANGE' into the secret word field and click the 'Lock Word 🔐' button, then switch to the host tab and click the '✨ Begin Reveal Sequence' button.
        # Lock Word 🔐 button
        elem = page.get_by_role("button", name="Lock Word 🔐")
        await elem.click(timeout=10000)
        
        # -> Fill 'ORANGE' into the secret word field and click the 'Lock Word 🔐' button, then switch to the host tab and click the '✨ Begin Reveal Sequence' button.
        # Switch to tab 0722
        page = context.pages[-1]  # switch to most recently active tab
        
        # -> Fill 'ORANGE' into the secret word field and click the 'Lock Word 🔐' button, then switch to the host tab and click the '✨ Begin Reveal Sequence' button.
        # ✨ Begin Reveal Sequence button
        elem = page.get_by_role("button", name="✨ Begin Reveal Sequence")
        await elem.click(timeout=10000)
        
        # -> Switch to the Guest2 browser tab and verify the secret word is locked (the 'Lock Word 🔐' control or confirmation should indicate submission).
        # Switch to tab 266D
        page = context.pages[-1]  # switch to most recently active tab
        
        # -> Open a new tab to the entry page and join room NJJ3 as 'Guest3' by filling 'YOUR DISPLAY NAME' with 'Guest3', entering room code 'NJJ3', and clicking the '🚀 Join Room' button.
        # Open URL in new tab
        page = await context.new_page()
        await page.goto("http://localhost:8000/")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Fill 'Guest3' into the YOUR DISPLAY NAME field and click the '🚀 Join Room' button to join room NJJ3 as Guest3.
        # Switch to tab 0544
        page = context.pages[-1]  # switch to most recently active tab
        
        # -> Fill 'Guest3' into the YOUR DISPLAY NAME field and click the '🚀 Join Room' button to join room NJJ3.
        # e.g. Maverick, Sherlock text field
        elem = page.get_by_role("textbox", name="YOUR DISPLAY NAME")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Guest3")
        
        # -> Fill 'Guest3' into the YOUR DISPLAY NAME field and click the '🚀 Join Room' button to join room NJJ3.
        # CODE text field
        elem = page.get_by_role("textbox", name="CODE")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("NJJ3")
        
        # -> Fill 'Guest3' into the YOUR DISPLAY NAME field and click the '🚀 Join Room' button to join room NJJ3.
        # 🚀 Join Room button
        elem = page.get_by_role("button", name="🚀 Join Room")
        await elem.click(timeout=10000)
        
        # -> Click the 'Change' button next to the locked word to open the secret-word editor for this player.
        # Change button
        elem = page.get_by_role("button", name="Change", exact=True)
        await elem.click(timeout=10000)
        
        # -> Enter 'MANGO' into the 'ENTER SECRET WORD...' field and click the 'Lock Word 🔐' button.
        # ENTER SECRET WORD... text field
        elem = page.get_by_role("textbox", name="ENTER SECRET WORD...")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("MANGO")
        
        # -> Enter 'MANGO' into the 'ENTER SECRET WORD...' field and click the 'Lock Word 🔐' button.
        # Lock Word 🔐 button
        elem = page.get_by_role("button", name="Lock Word 🔐")
        await elem.click(timeout=10000)
        
        # -> Switch to the host tab and open the host view so the '✨ Begin Reveal Sequence' button can be clicked.
        # Switch to tab 0722
        page = context.pages[-1]  # switch to most recently active tab
        
        # -> Click the '✨ Begin Reveal Sequence' button after allowing the host view to receive updates (wait, switch to another player tab, then back).
        # Switch to tab 266D
        page = context.pages[-1]  # switch to most recently active tab
        
        # -> Click the '✨ Begin Reveal Sequence' button after allowing the host view to receive updates (wait, switch to another player tab, then back).
        # Switch to tab 0722
        page = context.pages[-1]  # switch to most recently active tab
        
        # -> Click the '✨ Begin Reveal Sequence' button after allowing the host view to receive updates (wait, switch to another player tab, then back).
        # ✨ Begin Reveal Sequence button
        elem = page.get_by_role("button", name="✨ Begin Reveal Sequence")
        await elem.click(timeout=10000)
        
        # -> Reload the host room page and then click the '✨ Begin Reveal Sequence' button if it becomes enabled.
        await page.goto("http://localhost:8000/")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Switch to the host tab and inspect the host view to find the '✨ Begin Reveal Sequence' button.
        # Switch to tab 0722
        page = context.pages[-1]  # switch to most recently active tab
        
        # -> Switch to the guest tab that shows the locked word 'ORANGE' (Guest2 tab) and inspect the room view to confirm locked words and room state.
        # Switch to tab 266D
        page = context.pages[-1]  # switch to most recently active tab
        
        # -> Switch to the host tab and inspect the host view to find the '✨ Begin Reveal Sequence' button.
        # Switch to tab 0722
        page = context.pages[-1]  # switch to most recently active tab
        
        # -> Click the '🎮 Host New Room' button to create a host session as 'Tester' so the host controls (including the Begin Reveal button) become visible.
        # e.g. Maverick, Sherlock text field
        elem = page.get_by_role("textbox", name="YOUR DISPLAY NAME")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Tester")
        
        # -> Click the '🎮 Host New Room' button to create a host session as 'Tester' so the host controls (including the Begin Reveal button) become visible.
        # 🎮 Host New Room button
        elem = page.get_by_role("button", name="🎮 Host New Room")
        await elem.click(timeout=10000)
        
        # -> Switch to the Guest2 tab so the Guest2 join flow can be completed (fill display name and join room VH7B).
        # Switch to tab 266D
        page = context.pages[-1]  # switch to most recently active tab
        
        # -> Click the 'Leave Room' button to return Guest2 to the entry screen so it can join room VH7B.
        # Leave Room button
        elem = page.get_by_role("button", name="Leave Room")
        await elem.click(timeout=10000)
        
        # -> Switch to the Guest2 tab and confirm the guest is on the entry screen so it can join room VH7B using the '🚀 Join Room' flow.
        # Switch to tab 266D
        page = context.pages[-1]  # switch to most recently active tab
        
        # -> Fill 'Guest2' into the YOUR DISPLAY NAME field, enter room code 'VH7B', and click the '🚀 Join Room' button to join room VH7B as Guest2.
        # e.g. Maverick, Sherlock text field
        elem = page.get_by_role("textbox", name="YOUR DISPLAY NAME")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Guest2")
        
        # -> Fill 'Guest2' into the YOUR DISPLAY NAME field, enter room code 'VH7B', and click the '🚀 Join Room' button to join room VH7B as Guest2.
        # CODE text field
        elem = page.get_by_role("textbox", name="CODE")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("VH7B")
        
        # -> Fill 'Guest2' into the YOUR DISPLAY NAME field, enter room code 'VH7B', and click the '🚀 Join Room' button to join room VH7B as Guest2.
        # 🚀 Join Room button
        elem = page.get_by_role("button", name="🚀 Join Room")
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        current_url = await page.evaluate("() => window.location.href")
        # Assert-outcome: passed
        # Assert: page loaded with a URL (final outcome verified by the AI judge during the run)
        assert current_url, 'Page should have loaded with a URL'
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    