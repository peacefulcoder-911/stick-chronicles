#!/usr/bin/env python3
"""
Render high-energy motion clip for Kids Channel
Action: "Excited Leap & Pop Zoom" (2.5s vertical 1080x1920 60fps/30fps MP4)
"""

import sys
import subprocess
from pathlib import Path

def render_motion(image_path: str, output_path: str, duration: float = 2.5, fps: int = 30):
    img = Path(image_path).resolve()
    out = Path(output_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    
    total_frames = int(duration * fps)
    
    # 2.5s Motion Profile:
    # 1. Follows the jump upwards (panning from meadow up to dino)
    # 2. Dynamic punch-zoom accelerating toward the smiling dino face and sparkles
    # 3. Micro-bounce at the apex (sine modulation) for cartoon springiness
    
    # Using zoompan in FFmpeg:
    # z: zooms from 1.0 up to 1.28 with smooth easing
    # x: centered
    # y: tracks upwards from center-low to face level
    vf = (
        f"scale=1080:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920,"
        f"zoompan=z='min(1.0+0.30*(on/{total_frames})*(on/{total_frames})+0.02*sin(on*3.1415*4/{total_frames}),1.32)':"
        f"d={total_frames}:"
        f"x='iw/2-(iw/zoom/2)':"
        f"y='(ih/2-(ih/zoom/2)) - (ih*0.08*(on/{total_frames}))':"
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
    
    print(f"Rendering {duration}s motion clip to {out}...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print("FFmpeg stderr:", res.stderr)
        raise RuntimeError(f"FFmpeg failed: {res.stderr[-300:]}")
    print(f"✅ Motion clip successfully created: {out}")

if __name__ == "__main__":
    src_img = sys.argv[1] if len(sys.argv) > 1 else "/Users/vinaybt/.gemini/antigravity-ide/brain/4ac7fab2-6146-4a49-8f48-e3ffc3892ced/cute_baby_dino_1792773379657.jpg"
    out_mp4 = sys.argv[2] if len(sys.argv) > 2 else "/Users/vinaybt/.gemini/antigravity-ide/brain/4ac7fab2-6146-4a49-8f48-e3ffc3892ced/baby_dino_jump_motion.mp4"
    render_motion(src_img, out_mp4, duration=2.5, fps=30)
