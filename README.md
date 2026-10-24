# 🏃 Stick Chronicles (`stick-chronicles`)

> **Automated AI Short-Form Video Studio for Animated Stickman History & Ancient Trivia.**

Stick Chronicles is an end-to-end automated pipeline that generates high-retention 9:16 YouTube Shorts, TikToks, and Reels featuring animated stickman illustrations, Gemini Achird voiceover, and synchronized bold subtitles.

## 🌟 Episodes Produced
- 🦣 **How Cavemen Hunted Mammoths**: Megafauna trapping strategies & the human bait.
- 🔥 **The Day Cavemen Discovered Fire**: Lightning strikes, roasted meat, and the dawn of humanity.
- 📜 **Nalanda: The University That Attracted the World**: Ancient India's legendary international learning center.
- ⚔️ **Hiroo Onoda: The Soldier Who Fought for 29 Years**: The WWII holdout who refused to surrender until 1974.
- 💰 **Why Do We Pay Taxes?**: From ancient grain tribute to modern economies explained.

## 🛠️ Pipeline Architecture
```
stick-chronicles/
├── run_shorts_pipeline.py     # Master orchestrator
├── generate_tts_audio.py      # Gemini Achird voice TTS generation
├── build_short_video.py       # FFmpeg assembler with Ken Burns motion & bold subtitles
├── flow_image_generator.py    # Automated Google Flow visual asset generator
├── flow_i2v_playwright.py     # Image-to-Video AI animation via Playwright
├── watermark_engine.py        # Universal AI watermark remover & refiner
├── web_app.py                 # Gradio/FastAPI studio control UI
├── channel/
│   └── topics.md              # Planned video topics & production queue
└── videos/                    # Episode archives (scripts, storyboards, images)
```

## 🚀 Quick Start

### 1. Run the Pipeline
```bash
python3 run_shorts_pipeline.py --topic "How Cavemen Hunted Mammoths"
```

### 2. Generate Audio Only
```bash
python3 generate_tts_audio.py
```

### 3. Build & Render Video Only
```bash
python3 build_short_video.py how-cavemen-hunted-mammoths
```
