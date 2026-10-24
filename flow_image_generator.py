#!/usr/bin/env python3
"""
Google Flow Automated Image Generator via Playwright
----------------------------------------------------
Automates prompt entry, generation, and image retrieval on https://flow.google.com/
Uses persistent profile credentials stored in `./flow_chrome_profile`.
"""

import os
import sys
import time
import base64
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, BrowserContext

BASE_DIR = Path(__file__).parent.resolve()
PROFILE_DIR = BASE_DIR / "flow_chrome_profile"
DEFAULT_OUTPUT_DIR = BASE_DIR / "images"

class GoogleFlowGenerator:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.profile_dir = PROFILE_DIR
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.playwright = None
        self.context = None
        self.page = None

    def start_browser(self):
        """Starts persistent browser context using local Chrome."""
        self.playwright = sync_playwright().start()
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.profile_dir),
            channel="chrome",
            headless=self.headless,
            viewport={"width": 1440, "height": 900},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ]
        )
        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()

    def close(self):
        """Clean up browser resources."""
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()

    def ensure_authenticated(self):
        """Checks if session is active or requires initial login."""
        self.page.goto("https://flow.google.com/", wait_until="domcontentloaded")
        time.sleep(3)

        # Handle landing page redirect if needed
        create_btn = self.page.locator("text='Create with Google Flow'")
        if create_btn.is_visible():
            create_btn.click()
            time.sleep(3)

        if "accounts.google.com" in self.page.url:
            raise RuntimeError(
                "❌ Session not logged in!\n"
                "Please run `python init_flow_session.py` first to log in with your Google account."
            )

    def find_prompt_input(self):
        """Locates the prompt input area dynamically across Google Flow UI variations."""
        selectors = [
            "textarea",
            "div[contenteditable='true']",
            "input[type='text'][placeholder*='prompt' i]",
            "input[type='text'][placeholder*='describe' i]",
            "[aria-label*='prompt' i]",
            "[aria-label*='describe' i]",
            "input[type='text']",
        ]
        
        for sel in selectors:
            loc = self.page.locator(sel).first
            if loc.is_visible():
                return loc
                
        return None

    def generate_image(self, prompt: str, output_path: str, timeout_seconds: int = 60) -> str:
        """
        Sends prompt to Google Flow, waits for generation, and saves image to output_path.
        """
        out_file = Path(output_path).resolve()
        out_file.parent.mkdir(parents=True, exist_ok=True)

        print(f"\n[Google Flow] Generating image for prompt:\n  \"{prompt}\"")
        self.ensure_authenticated()

        # Step 1: Locate prompt input
        input_element = self.find_prompt_input()
        if not input_element:
            # Take debug screenshot
            debug_shot = BASE_DIR / "debug_flow_page.png"
            self.page.screenshot(path=str(debug_shot))
            raise RuntimeError(
                f"Could not locate prompt input on Google Flow. Saved debug screenshot to {debug_shot}"
            )

        # Step 2: Enter prompt
        input_element.click()
        input_element.fill(prompt)
        time.sleep(1)

        # Step 3: Trigger generation (Click Generate or press Enter)
        generate_btn = self.page.locator(
            "button:has-text('Generate'), button:has-text('Create'), button[aria-label*='generate' i]"
        ).first
        
        if generate_btn.is_visible():
            generate_btn.click()
        else:
            input_element.press("Enter")

        print("[Google Flow] Prompt submitted. Waiting for image generation...")

        # Step 4: Wait for image generation result
        start_time = time.time()
        generated_img = None

        while time.time() - start_time < timeout_seconds:
            # Look for newly rendered preview images or canvas
            candidates = self.page.locator("img[src*='blob:'], img[src*='googleusercontent'], img[src*='data:image'], canvas")
            count = candidates.count()
            if count > 0:
                # Find the most prominent candidate
                for i in range(count):
                    candidate = candidates.nth(i)
                    if candidate.is_visible():
                        box = candidate.bounding_box()
                        if box and box["width"] > 200 and box["height"] > 200:
                            generated_img = candidate
                            break
            if generated_img:
                break
            time.sleep(2)

        if not generated_img:
            # Fallback: capture page snapshot or error
            debug_shot = BASE_DIR / "debug_generation_timeout.png"
            self.page.screenshot(path=str(debug_shot))
            raise TimeoutError(f"Image generation timed out after {timeout_seconds}s. Debug snapshot: {debug_shot}")

        # Step 5: Save image
        src = generated_img.get_attribute("src")
        if src and src.startswith("data:image"):
            # Base64 image
            header, encoded = src.split(",", 1)
            img_data = base64.b64decode(encoded)
            with open(out_file, "wb") as f:
                f.write(img_data)
        else:
            # Element screenshot preserves exact pixel rendering
            generated_img.screenshot(path=str(out_file))

        print(f"✅ Image successfully saved to: {out_file}\n")
        return str(out_file)

def main():
    parser = argparse.ArgumentParser(description="Automate Google Flow image generation")
    parser.add_argument("--prompt", required=True, help="Image prompt text")
    parser.add_argument("--output", default="output.png", help="Path to save generated image")
    parser.add_argument("--headless", action="store_true", help="Run browser headlessly")
    args = parser.parse_args()

    gen = GoogleFlowGenerator(headless=args.headless)
    try:
        gen.start_browser()
        gen.generate_image(prompt=args.prompt, output_path=args.output)
    finally:
        gen.close()

if __name__ == "__main__":
    main()
