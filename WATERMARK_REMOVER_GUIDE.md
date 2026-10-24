# WatermarkX AI — Universal Watermark Remover

A high-performance tool suite to remove any watermark, logo, stamp, or text overlay from any image cleanly.

---

## 🚀 Ways to Use

### 1. Interactive Web Application Studio (Recommended)

Launch the web studio with a single command:

```bash
python watermark_remover.py --web
```
Or directly:
```bash
python web_app.py
```
Open **[http://localhost:7860](http://localhost:7860)** in your browser.

#### Studio Features:
- 🖼️ **Drag & Drop / Clipboard Paste**: Drop any image (`.png`, `.jpg`, `.webp`, `.bmp`) or press `Cmd+V / Ctrl+V` to paste from clipboard.
- 🖌️ **Smart Brush Tool**: Freely paint over any watermark shape with adjustable brush size (`6px` to `120px`).
- 🔲 **Box / Rectangle Tool**: Drag a rectangle to box any watermark in one quick motion.
- 🧹 **Eraser Tool & Undo Stack**: Cleanly refine your mask or undo brush strokes.
- ⚡ **Auto-Detect Watermark (CV)**: 1-click autonomous computer vision detector that scans edge densities and contrast gradients.
- 🤖 **AI Vision Detect (Gemini)**: Uses Gemini 2.5 Flash Vision API to identify watermarks and bounding boxes.
- 📐 **1-Click Presets**:
  - `↘️ Bottom-Right` (Standard for Google Flow, Midjourney, DALL-E, TikTok, AI images)
  - `↙️ Bottom-Left`
  - `↗️ Top-Right`
  - `↖️ Top-Left`
  - `➖ Bottom Banner` (Subtitles, handles, bottom strips)
  - `🌐 Full Tiled Grid` (Stock photo diagonal watermarks)
- 🎛️ **Inpainting Algorithms**:
  - **Multi-Scale Laplacian PDE** (Default: sub-50ms ultra-fast gradient & ambient lighting continuation)
  - **Texture Match Synthesis** (Recreates natural grain, fabric, foliage, and micro-textures)
  - **Semi-Transparent Inversion** (Recovers details trapped beneath semi-transparent watermarks)
  - **Directional Diffusion** (Maintains crisp edge and line continuity)
- 🔍 **Interactive Split Comparison Slider**: Drag the vertical slider left and right to inspect the cleaned image side-by-side with the original.
- 💾 **Export**: One-click **Download Clean Image** (lossless full resolution) or **Copy to Clipboard**.

---

### 2. Command Line Interface (CLI)

Remove watermarks directly from terminal or automation scripts:

#### Quick Corner Removal (Google Flow / AI Images):
```bash
python watermark_remover.py input.png -o clean.png --preset bottom-right
```

#### Autonomous Auto-Detection:
```bash
python watermark_remover.py input.png -o clean.png --auto
```

#### AI Vision Auto-Detection (Gemini):
```bash
python watermark_remover.py input.png -o clean.png --ai
```

#### Custom Bounding Box (`ymin,xmin,ymax,xmax` in normalized 0–1 or pixels):
```bash
python watermark_remover.py input.png -o clean.png --box 0.88,0.75,0.98,0.98
```

#### Batch Clean an Entire Directory:
```bash
python watermark_remover.py ./watermarked_folder/ -o ./clean_folder/ --preset bottom-right --batch
```

#### Generate Side-by-Side Comparison Image:
```bash
python watermark_remover.py input.png -o clean.png --preset bottom-right --compare
```

#### Algorithm Selection:
```bash
# Options: pde_multiscale, texture_synthesis, alpha_deblend, directional_diffusion
python watermark_remover.py input.png -o clean.png --method texture_synthesis --dilation 5
```

---

### 3. Python API Integration

```python
from PIL import Image
from watermark_engine import WatermarkEngine

engine = WatermarkEngine()
img = Image.open("photo.png")

# 1. Generate preset mask or auto-detect
mask = engine.get_preset_mask(img.width, img.height, "bottom-right")

# 2. Inpaint and restore background
clean_img = engine.inpaint(img, mask, method="pde_multiscale", dilation=4)
clean_img.save("photo_clean.png")
```
