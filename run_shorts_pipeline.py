#!/usr/bin/env python3
"""
Full Automated Pipeline for Stickman YouTube Shorts:
1. Generates high-quality script on ancient/history topics.
2. Generates TTS audio using Gemini Achird voice.
3. Maps script into 10-12 high-motion scene prompts and generates image assets.
4. Assembles 9:16 vertical video with Ken Burns pan/zoom motion, audio, and styled subtitles.
"""

import os
import sys
import argparse
import subprocess
import pathlib

def run_pipeline(topic_title=None):
    base_dir = pathlib.Path(__file__).parent.absolute()
    
    # 1. Check or set topic
    topics_file = base_dir / "channel" / "topics.md"
    if topic_title:
        topics_file.parent.mkdir(parents=True, exist_ok=True)
        topics_file.write_text(f"# Channel Topics\n\nTitle: {topic_title}\n", encoding="utf-8")
        print(f"Set topic to: {topic_title}")

    # 2. Run TTS Audio Generator
    print("\n[Step 1/3] Generating Audio with Gemini Achird TTS...")
    audio_res = subprocess.run([sys.executable, str(base_dir / "generate_tts_audio.py")], check=True)

    # 3. Build Video with Motion & Subtitles
    print("\n[Step 2/3] Rendering Video with Ken Burns Motion & Subtitles...")
    video_res = subprocess.run([sys.executable, str(base_dir / "build_short_video.py")], check=True)

    print("\n[Step 3/3] Complete! Check out_shorts/ for your finished video.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate complete Stickman YouTube Short")
    parser.add_argument("--topic", help="Topic title for the short", default=None)
    args = parser.parse_args()
    run_pipeline(args.topic)
