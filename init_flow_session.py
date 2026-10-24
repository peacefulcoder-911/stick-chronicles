#!/usr/bin/env python3
"""
Initialize Google Flow Playwright Session
-----------------------------------------
Launches Google Chrome with a persistent user data profile.
Allows you to log in to your Google Account once with 2FA/passkey.
Once logged in, the session is saved permanently in `./flow_chrome_profile`
so all subsequent automation runs can operate automatically.
"""

import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).parent.resolve()
PROFILE_DIR = BASE_DIR / "flow_chrome_profile"

def init_session():
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n=======================================================")
    print(f"🚀 Launching Google Chrome to initialize Google Flow session")
    print(f"📁 Session Storage: {PROFILE_DIR}")
    print(f"=======================================================\n")

    with sync_playwright() as p:
        # Launch persistent Chrome browser
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            channel="chrome",  # Uses local Google Chrome installation
            headless=False,
            viewport={"width": 1280, "height": 900},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ]
        )

        page = context.pages[0] if context.pages else context.new_page()
        
        print("🌐 Navigating to https://flow.google.com/ ...")
        page.goto("https://flow.google.com/", wait_until="domcontentloaded")
        time.sleep(2)

        # Check if landed on the landing page with 'Create with Google Flow' button
        create_button = page.locator("text='Create with Google Flow'")
        if create_button.is_visible():
            print("👉 Clicking 'Create with Google Flow' button...")
            create_button.click()
            time.sleep(2)

        # Check if redirected to Google Sign-In
        if "accounts.google.com" in page.url or "signin" in page.url:
            print("\n" + "=" * 60)
            print("🔑 ACTION REQUIRED: Please log in to your Google account")
            print("   in the open Chrome window.")
            print("   Complete 2FA / verification if prompted.")
            print("=" * 60 + "\n")
            
            # Wait for user to complete login and return to flow.google.com
            try:
                page.wait_for_url(
                    lambda url: "flow.google.com" in url and "accounts.google.com" not in url,
                    timeout=300000  # 5 minutes wait
                )
                print("\n✅ Sign-in detected! Waiting for Google Flow dashboard to load...")
                time.sleep(5)
            except Exception as e:
                print(f"\n⚠️ Timeout or login check error: {e}")
                print("If you have finished logging in, you can proceed.")

        # Confirm we are on flow.google.com
        print(f"\n🎉 Current URL: {page.url}")
        print("💾 Your Google session has been saved to ./flow_chrome_profile")
        print("You can now run automated image generation without having to log in again!\n")
        
        input("Press [Enter] in this terminal to close the browser...")
        context.close()

if __name__ == "__main__":
    init_session()
