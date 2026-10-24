#!/usr/bin/env python3
"""
Google Flow Image-to-Video (I2V) Automated Generator via Playwright
-------------------------------------------------------------------
Takes an input image (e.g. a character) + an action prompt (e.g. "dancing happily, waving arms"),
uploads it to Google Flow (Veo / VideoFX), triggers true generative video synthesis,
and downloads the rendered .mp4 video where the character literally moves and dances.

Usage:
    python flow_i2v_playwright.py --image path/to/character.jpg --prompt "dancing and waving hands" --output out_shorts/dance.mp4
"""

import os
import sys
import time
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright, FileChooser, TimeoutError as PlaywrightTimeoutError

BASE_DIR = Path(__file__).parent.resolve()
PROFILE_DIR = BASE_DIR / "flow_chrome_profile"
DEFAULT_OUT_DIR = BASE_DIR / "out_shorts"

class GoogleFlowVideoGenerator:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.profile_dir = PROFILE_DIR
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.playwright = None
        self.context = None
        self.page = None

    def start_browser(self):
        """Launches persistent Chrome browser with your saved profile."""
        print(f"🚀 Launching Chrome using persistent profile: {self.profile_dir}")
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
        """Clean up resources."""
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()

    def navigate_and_verify_login(self):
        """Navigates to Google Flow and ensures session is authenticated."""
        print("🌐 Opening https://flow.google.com/ ...")
        self.page.goto("https://flow.google.com/", wait_until="domcontentloaded")
        time.sleep(3)

        # Handle landing page redirect if present
        create_btn = self.page.locator("text='Create with Google Flow'")
        if create_btn.is_visible():
            create_btn.click()
            time.sleep(3)

        if "accounts.google.com" in self.page.url:
            print("\n" + "=" * 60)
            print("🔑 ACTION REQUIRED: Please log in to your Google account in the Chrome window.")
            print("=" * 60 + "\n")
            self.page.wait_for_url(
                lambda url: "flow.google.com" in url and "accounts.google.com" not in url,
                timeout=300000
            )
            print("✅ Login completed! Continuing to Flow workspace...")
            time.sleep(4)

    def switch_to_video_mode(self):
        """Switches to Video / Animate / Image-to-Video tab on Google Flow."""
        video_selectors = [
            "button:has-text('Video')",
            "tab:has-text('Video')",
            "[aria-label*='video' i]",
            "button:has-text('Animate')",
            "button:has-text('Motion')",
            "button:has-text('Veo')"
        ]
        
        for sel in video_selectors:
            loc = self.page.locator(sel).first
            if loc.is_visible():
                print(f"🎬 Switching mode: clicked '{sel}'")
                loc.click()
                time.sleep(2)
                break

    def upload_input_image(self, image_path: Path):
        """Uploads the source character image into Google Flow's image input."""
        print(f"📤 Uploading character image: {image_path.name}")
        
        # Check for standard hidden file input
        file_input = self.page.locator("input[type='file']").first
        if file_input.count() > 0:
            file_input.set_input_files(str(image_path))
            time.sleep(2)
            return True

        # Check for file chooser button / drag-drop target
        upload_btn_selectors = [
            "button:has-text('Upload')",
            "button:has-text('Image')",
            "[aria-label*='upload' i]",
            "[aria-label*='add image' i]",
            ".dropzone",
            "[data-testid*='upload']"
        ]
        
        for sel in upload_btn_selectors:
            btn = self.page.locator(sel).first
            if btn.is_visible():
                with self.page.expect_file_chooser(timeout=5000) as fc_info:
                    btn.click()
                file_chooser = fc_info.value
                file_chooser.set_files(str(image_path))
                time.sleep(2)
                return True

        print("⚠️ Direct file input element not immediately found; attempting drag-and-drop or prompt attachment...")
        return False

    def enter_action_prompt(self, action_prompt: str):
        """Enters the desired movement/dance action prompt."""
        print(f"✍️ Entering action prompt: \"{action_prompt}\"")
        
        input_selectors = [
            "textarea",
            "div[contenteditable='true']",
            "input[type='text'][placeholder*='prompt' i]",
            "input[type='text'][placeholder*='action' i]",
            "input[type='text'][placeholder*='motion' i]",
            "input[type='text'][placeholder*='describe' i]",
            "[aria-label*='prompt' i]",
            "input[type='text']"
        ]
        
        for sel in input_selectors:
            loc = self.page.locator(sel).first
            if loc.is_visible():
                loc.click()
                loc.fill(action_prompt)
                time.sleep(1)
                return loc

        raise RuntimeError("Could not find prompt input field on Google Flow.")

    def trigger_generation(self):
        """Clicks the Generate / Animate Video button."""
        print("⚡ Triggering video generation...")
        btn_selectors = [
            "button:has-text('Generate')",
            "button:has-text('Create')",
            "button:has-text('Animate')",
            "button[aria-label*='generate' i]",
            "button[aria-label*='create' i]"
        ]
        
        for sel in btn_selectors:
            loc = self.page.locator(sel).first
            if loc.is_visible():
                loc.click()
                print(f"👉 Clicked generation button: '{sel}'")
                return
                
        # Fallback: Enter key
        self.page.keyboard.press("Enter")

    def wait_and_download_video(self, output_path: Path, max_wait_seconds: int = 240) -> Path:
        """
        Monitors Google Flow until the video is rendered by Veo,
        then downloads the resulting MP4 file.
        """
        print(f"⏳ Waiting for generative AI video rendering (up to {max_wait_seconds}s)...")
        start_time = time.time()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        video_element = None
        while time.time() - start_time < max_wait_seconds:
            # Check for rendered <video> elements
            videos = self.page.locator("video")
            if videos.count() > 0:
                for i in range(videos.count()):
                    v = videos.nth(i)
                    src = v.get_attribute("src")
                    if src and ("blob:" in src or "googleusercontent" in src or "storage" in src or ".mp4" in src):
                        video_element = v
                        break
            
            # Check for download button
            download_btn = self.page.locator("button[aria-label*='download' i], button:has-text('Download')").first
            if download_btn.is_visible() and video_element:
                break
                
            time.sleep(3)

        if not video_element:
            debug_path = BASE_DIR / "debug_video_render.png"
            self.page.screenshot(path=str(debug_path))
            raise TimeoutError(f"Video generation timed out after {max_wait_seconds}s. Screenshot: {debug_path}")

        print("🎬 Generative video detected! Downloading...")

        # Method 1: Click download button if available
        download_btn = self.page.locator("button[aria-label*='download' i], button:has-text('Download')").first
        if download_btn.is_visible():
            try:
                with self.page.expect_download(timeout=15000) as download_info:
                    download_btn.click()
                download = download_info.value
                download.save_as(str(output_path))
                print(f"✅ Video downloaded via download button: {output_path}")
                return output_path
            except Exception as e:
                print(f"Notice: download button click skipped ({e}), falling back to direct video stream extraction...")

        # Method 2: Extract video buffer via JS evaluate fetch
        src_url = video_element.get_attribute("src")
        if src_url:
            print(f"Extracting video source: {src_url[:60]}...")
            video_bytes = self.page.evaluate("""async (url) => {
                const response = await fetch(url);
                const buffer = await response.arrayBuffer();
                let binary = '';
                const bytes = new Uint8Array(buffer);
                const len = bytes.byteLength;
                for (let i = 0; i < len; i++) {
                    binary += String.fromCharCode(bytes[i]);
                }
                return btoa(binary);
            }""", src_url)
            
            import base64
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(video_bytes))
            print(f"✅ Video saved directly from stream: {output_path}")
            return output_path

        raise RuntimeError("Failed to extract video file from page.")

    def convert_image_to_video(self, image_path: str, action_prompt: str, output_path: str) -> str:
        """Full pipeline: image + action prompt -> animated .mp4"""
        img = Path(image_path).resolve()
        out = Path(output_path).resolve()

        if not img.exists():
            raise FileNotFoundError(f"Input image not found: {img}")

        self.navigate_and_verify_login()
        self.switch_to_video_mode()
        self.upload_input_image(img)
        self.enter_action_prompt(action_prompt)
        self.trigger_generation()
        result_file = self.wait_and_download_video(out)
        return str(result_file)

def main():
    parser = argparse.ArgumentParser(description="Convert Image to Generative AI Video via Google Flow")
    parser.add_argument("--image", required=True, help="Path to input character image")
    parser.add_argument("--prompt", required=True, help="Action/movement prompt (e.g. 'dancing happily, waving hands')")
    parser.add_argument("--output", default="out_shorts/character_dance.mp4", help="Output .mp4 video path")
    parser.add_argument("--headless", action="store_true", help="Run browser headlessly")
    args = parser.parse_args()

    generator = GoogleFlowVideoGenerator(headless=args.headless)
    try:
        generator.start_browser()
        out = generator.convert_image_to_video(
            image_path=args.image,
            action_prompt=args.prompt,
            output_path=args.output
        )
        print(f"\n🎉 DONE! Generated actual video at: {out}")
    finally:
        generator.close()

if __name__ == "__main__":
    main()
