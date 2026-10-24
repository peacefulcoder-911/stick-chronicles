#!/usr/bin/env python3
"""
Render Motion Variation 2: Bouncy Float & Sparkle Pan (2.5s vertical 1080x1920 30fps MP4)
"""
import sys
import subprocess
from pathlib import Path

def render_float_motion(image_path: str, output_path: str, duration: float = 2.5, fps: int = 30):
    img = Path(image_path).resolve()
    out = Path(output_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    
    total_frames = int(duration * fps)
    
    # Motion Profile: Playful float & camera tilt/sway simulating gentle airborne bobbing
    vf = (
        f"scale=1080:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920,"
        f"zoompan=z='1.14 + 0.05*sin(on*3.1415*2/{total_frames})':"
        f"d={total_frames}:"
        f"x='iw/2-(iw/zoom/2) + iw*0.025*sin(on*3.1415*3/{total_frames})':"
        f"y='ih/2-(ih/zoom/2) - ih*0.04*cos(on*3.1415*2/{total_frames})':"
        f"s=1080x1920:fps={fps}"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(img),
        "-vf", vf,
        "-t", f"{duration:.2f}",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        str(out)
    ]
    
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    print(f"✅ Float motion clip successfully created: {out}")

if __name__ == "__main__":
    src_img = sys.argv[1] if len(sys.argv) > 1 else "/Users/vinaybt/.gemini/antigravity-ide/brain/4ac7fab2-6146-4a49-8f48-e3ffc3892ced/cute_baby_dino_1792773379657.jpg"
    out_mp4 = sys.argv[2] if len(sys.argv) > 2 else "/Users/vinaybt/.gemini/antigravity-ide/brain/4ac7fab2-6146-4a49-8f48-e3ffc3892ced/baby_dino_bouncy_float.mp4"
    render_float_motion(src_img, out_mp4, duration=2.5, fps=30)
