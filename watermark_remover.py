#!/usr/bin/env python3
"""
Universal Watermark Remover CLI
===============================
Command-line interface to remove any watermark from any image or directory of images.

Usage Examples:
    # 1. Quick remove with standard bottom-right preset (Flow/Midjourney/TikTok/AI)
    python watermark_remover.py input.png -o clean.png --preset bottom-right

    # 2. Fully automated detection and removal
    python watermark_remover.py input.png -o clean.png --auto

    # 3. AI-powered detection (Gemini Vision)
    python watermark_remover.py input.png -o clean.png --ai

    # 4. Custom bounding box (ymin, xmin, ymax, xmax in pixels or normalized 0-1)
    python watermark_remover.py input.png -o clean.png --box 0.85,0.75,0.98,0.98

    # 5. Batch clean an entire folder
    python watermark_remover.py ./watermarked_images/ -o ./clean_images/ --preset bottom-right --batch

    # 6. Generate side-by-side comparison image
    python watermark_remover.py input.png -o clean.png --preset bottom-right --compare

    # 7. Launch Interactive Web Application Studio
    python watermark_remover.py --web
"""

import sys
import os
import time
import argparse
from pathlib import Path
from typing import List

import numpy as np
from PIL import Image

from watermark_engine import WatermarkEngine

def parse_box(box_str: str, width: int, height: int) -> np.ndarray:
    """Parses 'ymin,xmin,ymax,xmax' either as pixel or normalized float values."""
    parts = [float(p.strip()) for p in box_str.split(",")]
    if len(parts) != 4:
        raise ValueError("Box must be 4 comma-separated numbers: ymin,xmin,ymax,xmax")
    
    ymin, xmin, ymax, xmax = parts
    # Check if normalized 0.0 - 1.0
    if ymax <= 1.0 and xmax <= 1.0:
        y1, y2 = int(ymin * height), int(ymax * height)
        x1, x2 = int(xmin * width), int(xmax * width)
    else:
        y1, y2 = int(ymin), int(ymax)
        x1, x2 = int(xmin), int(xmax)

    mask = np.zeros((height, width), dtype=bool)
    mask[max(0, y1):min(height, y2), max(0, x1):min(width, x2)] = True
    return mask

def create_comparison(orig: Image.Image, clean: Image.Image) -> Image.Image:
    """Creates a side-by-side comparison with label headers."""
    w, h = orig.size
    comp = Image.new("RGB", (w * 2 + 10, h), (18, 24, 38))
    comp.paste(orig, (0, 0))
    comp.paste(clean, (w + 10, 0))
    return comp

def process_file(
    engine: WatermarkEngine,
    input_path: Path,
    output_path: Path,
    preset: str = None,
    auto: bool = False,
    ai: bool = False,
    box: str = None,
    method: str = "pde_multiscale",
    dilation: int = 4,
    compare: bool = False
) -> bool:
    try:
        t0 = time.time()
        img = Image.open(input_path).convert("RGB")
        w, h = img.size
        
        mask = np.zeros((h, w), dtype=bool)

        if box:
            mask = parse_box(box, w, h)
        elif ai:
            res = engine.auto_detect_watermarks_ai(img)
            mask = res["mask"]
            print(f"  [AI Detection] Found {len(res.get('detected_boxes', []))} watermark region(s)")
        elif auto:
            res = engine.auto_detect_watermarks_cv(img)
            mask = res["mask"]
            print(f"  [CV Detection] Found {len(res.get('detected_boxes', []))} watermark region(s)")
        elif preset:
            mask = engine.get_preset_mask(w, h, preset)
        else:
            # Default to auto
            res = engine.auto_detect_watermarks_cv(img)
            mask = res["mask"]

        if not np.any(mask):
            print(f"  ⚠️ No watermark detected or mask empty for {input_path.name}. Outputting original.")
            clean_img = img.copy()
        else:
            clean_img = engine.inpaint(img, mask, method=method, dilation=dilation)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if compare:
            comp_path = output_path.with_name(f"{output_path.stem}_comparison{output_path.suffix}")
            create_comparison(img, clean_img).save(comp_path, quality=95)
            print(f"  [Comparison] Saved: {comp_path}")

        # Preserve format / quality
        if output_path.suffix.lower() in [".jpg", ".jpeg"]:
            clean_img.save(output_path, "JPEG", quality=98)
        else:
            clean_img.save(output_path, "PNG")

        elapsed = time.time() - t0
        print(f"  ✅ Cleaned: {input_path.name} -> {output_path.name} ({elapsed:.3f}s)")
        return True
    except Exception as e:
        print(f"  ❌ Error processing {input_path.name}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Universal Watermark Remover - Remove any watermark from any image cleanly."
    )
    parser.add_argument("input", nargs="?", help="Input image file or folder")
    parser.add_argument("-o", "--output", help="Output image file or folder")
    parser.add_argument("--preset", choices=["bottom-right", "bottom-left", "top-right", "top-left", "bottom-banner", "full-tiled"],
                        help="Geometry preset for watermark removal")
    parser.add_argument("--auto", action="store_true", help="Auto-detect watermark using computer vision")
    parser.add_argument("--ai", action="store_true", help="Auto-detect watermark using Gemini AI Vision")
    parser.add_argument("--box", help="Custom bounding box: ymin,xmin,ymax,xmax (e.g. 0.85,0.75,0.98,0.98)")
    parser.add_argument("--method", choices=["pde_multiscale", "texture_synthesis", "alpha_deblend", "directional_diffusion"],
                        default="pde_multiscale", help="Inpainting algorithm")
    parser.add_argument("--dilation", type=int, default=4, help="Mask dilation radius in pixels (default: 4)")
    parser.add_argument("--compare", action="store_true", help="Save side-by-side comparison image")
    parser.add_argument("--batch", action="store_true", help="Process directory of images")
    parser.add_argument("--web", action="store_true", help="Launch interactive Web Application Studio")
    parser.add_argument("--port", type=int, default=7860, help="Web application port (default: 7860)")

    args = parser.parse_args()

    if args.web:
        from web_app import launch_web_app
        launch_web_app(port=args.port)
        return

    if not args.input:
        parser.print_help()
        sys.exit(1)

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"❌ Input does not exist: {in_path}")
        sys.exit(1)

    engine = WatermarkEngine()

    if in_path.is_dir() or args.batch:
        out_dir = Path(args.output or (in_path.parent / f"{in_path.name}_clean"))
        out_dir.mkdir(parents=True, exist_ok=True)
        
        valid_exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}
        images = [f for f in in_path.iterdir() if f.suffix.lower() in valid_exts]
        
        print(f"\n[Watermark Remover] Processing {len(images)} images in {in_path} -> {out_dir}\n")
        success = 0
        t0 = time.time()
        for f in images:
            dest = out_dir / f.name
            if process_file(engine, f, dest, preset=args.preset, auto=args.auto, ai=args.ai,
                            box=args.box, method=args.method, dilation=args.dilation, compare=args.compare):
                success += 1
                
        total_time = time.time() - t0
        print(f"\n🎉 Done! Processed {success}/{len(images)} images in {total_time:.2f}s ({total_time / max(1, len(images)):.2f}s/image)")
    else:
        out_file = Path(args.output or (in_path.parent / f"{in_path.stem}_clean{in_path.suffix}"))
        print(f"\n[Watermark Remover] Processing {in_path} -> {out_file}...")
        process_file(engine, in_path, out_file, preset=args.preset, auto=args.auto, ai=args.ai,
                     box=args.box, method=args.method, dilation=args.dilation, compare=args.compare)

if __name__ == "__main__":
    main()
