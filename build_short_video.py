import os
import sys
import json
import wave
import pathlib
import subprocess
from datetime import timedelta

def format_ass_time(seconds):
    td = timedelta(seconds=seconds)
    hours = int(td.total_seconds() // 3600)
    minutes = int((td.total_seconds() % 3600) // 60)
    secs = int(td.total_seconds() % 60)
    centis = int(round((td.total_seconds() - int(td.total_seconds())) * 100))
    if centis >= 100:
        centis = 99
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"

def get_audio_duration(audio_path):
    with wave.open(str(audio_path), "rb") as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        return frames / float(rate)

def generate_ass_subtitles(dialogues, output_ass_path):
    ass_template = """[Script Info]
Title: Shorts Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,62,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,2,0,1,6,3,2,60,60,420,1
Style: Accent,Arial Black,66,&H0000E5FF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,2,0,1,7,4,2,60,60,420,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for d in dialogues:
        start_str = format_ass_time(d["start"])
        end_str = format_ass_time(d["end"])
        text = d["text"].upper()
        style = d.get("style", "Default")
        events.append(f"Dialogue: 0,{start_str},{end_str},{style},,0,0,0,,{text}")

    full_ass = ass_template + "\n".join(events) + "\n"
    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(full_ass)

def render_scene_clip(image_path, duration, output_path, motion_type="zoom_in"):
    fps = 30
    total_frames = int(duration * fps)
    
    if motion_type == "zoom_in":
        vf = (
            f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            f"zoompan=z='min(zoom+0.0018,1.18)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps={fps}"
        )
    elif motion_type == "zoom_out":
        vf = (
            f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            f"zoompan=z='if(lte(zoom,1.0),1.18,max(1.001,zoom-0.0018))':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps={fps}"
        )
    elif motion_type == "pan_up":
        vf = (
            f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            f"zoompan=z='1.12':d={total_frames}:x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(1-on/{total_frames})':s=1080x1920:fps={fps}"
        )
    elif motion_type == "pan_down":
        vf = (
            f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            f"zoompan=z='1.12':d={total_frames}:x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(on/{total_frames})':s=1080x1920:fps={fps}"
        )
    elif motion_type == "dramatic_punch":
        vf = (
            f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            f"zoompan=z='min(zoom+0.0035,1.25)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps={fps}"
        )
    else:
        vf = (
            f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            f"zoompan=z='min(zoom+0.0012,1.10)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps={fps}"
        )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(image_path),
        "-vf", vf,
        "-t", f"{duration:.3f}",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        str(output_path)
    ]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg failed for {image_path}: {res.stderr[:200]}")

def build_short_video(video_id=None):
    script_dir = pathlib.Path(__file__).parent.absolute()
    
    if not video_id:
        topics_file = script_dir / "channel" / "topics.md"
        if topics_file.exists():
            for line in topics_file.read_text().splitlines():
                if line.startswith("Title:"):
                    title = line[len("Title:"):].strip()
                    import re
                    video_id = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
                    break
        if not video_id:
            video_id = "how-cavemen-hunted-mammoths"

    video_dir = script_dir / "videos" / video_id
    images_dir = video_dir / "images"
    audio_path = script_dir / "audio" / f"{video_id}.wav"
    out_dir = script_dir / "out_shorts"
    out_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = video_dir / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    total_duration = get_audio_duration(audio_path)
    print(f"Building video for '{video_id}'...")
    print(f"Total audio duration: {total_duration:.2f}s")

    if "tax" in video_id:
        scenes = [
            {"img": "scene_01.jpg", "start": 0.00,  "end": 3.30,  "motion": "zoom_in"},
            {"img": "scene_02.jpg", "start": 3.30,  "end": 6.40,  "motion": "dramatic_punch"},
            {"img": "scene_03.jpg", "start": 6.40,  "end": 13.00, "motion": "pan_up"},
            {"img": "scene_04.jpg", "start": 13.00, "end": 16.00, "motion": "zoom_in"},
            {"img": "scene_05.jpg", "start": 16.00, "end": 20.30, "motion": "pan_up"},
            {"img": "scene_06.jpg", "start": 20.30, "end": 27.80, "motion": "zoom_out"},
            {"img": "scene_07.jpg", "start": 27.80, "end": 34.00, "motion": "dramatic_punch"},
            {"img": "scene_08.jpg", "start": 34.00, "end": 42.00, "motion": "pan_down"},
            {"img": "scene_09.jpg", "start": 42.00, "end": 48.00, "motion": "zoom_in"},
            {"img": "scene_10.jpg", "start": 48.00, "end": 52.00, "motion": "pan_up"},
            {"img": "scene_11.jpg", "start": 52.00, "end": total_duration, "motion": "dramatic_punch"}
        ]
        dialogues = [
            {"start": 0.00,  "end": 1.80,  "text": "IMAGINE EARNING ₹100...", "style": "Default"},
            {"start": 1.80,  "end": 3.20,  "text": "YOU WANT TO KEEP ALL OF IT!", "style": "Default"},
            {"start": 3.30,  "end": 5.20,  "text": "BUT THE GOVERNMENT TAKES A PORTION.", "style": "Accent"},
            {"start": 5.20,  "end": 6.40,  "text": "WHY?", "style": "Accent"},
            {"start": 6.40,  "end": 10.00, "text": "BECAUSE THE ROADS YOU DRIVE ON...", "style": "Default"},
            {"start": 10.00, "end": 13.00, "text": "THE SCHOOLS CHILDREN ATTEND...", "style": "Default"},
            {"start": 13.00, "end": 16.00, "text": "AND HOSPITALS WE DEPEND ON COST MONEY!", "style": "Accent"},
            {"start": 16.00, "end": 20.30, "text": "TAXES ARE HOW THE GOVERNMENT FUNDS THEM.", "style": "Default"},
            {"start": 20.30, "end": 23.50, "text": "YOU EARN MONEY, BUY THINGS, OWN PROPERTY...", "style": "Default"},
            {"start": 23.50, "end": 27.80, "text": "YOU PAY DIFFERENT TAXES ALONG THE WAY.", "style": "Default"},
            {"start": 27.80, "end": 31.00, "text": "BUYING A ₹1,000 PRODUCT WITH 18% GST...", "style": "Accent"},
            {"start": 31.00, "end": 34.00, "text": "BECOMES ₹1,180! THE ₹180 IS TAX.", "style": "Accent"},
            {"start": 34.00, "end": 38.00, "text": "NOT EVERYONE PAYS THE SAME AMOUNT.", "style": "Default"},
            {"start": 38.00, "end": 42.00, "text": "INCOME TAX DEPENDS ON WHAT YOU EARN.", "style": "Default"},
            {"start": 42.00, "end": 45.00, "text": "AND BUSINESSES PAY ON THEIR PROFITS.", "style": "Default"},
            {"start": 45.00, "end": 48.00, "text": "TAXES DON'T JUST DISAPPEAR FROM YOUR POCKET.", "style": "Accent"},
            {"start": 48.00, "end": 52.00, "text": "THEY BUILD OUR NATION'S INFRASTRUCTURE!", "style": "Default"},
            {"start": 52.00, "end": total_duration, "text": "THE REAL QUESTION: HOW WELL IS IT BEING SPENT?", "style": "Accent"}
        ]
    elif "onoda" in video_id:
        scenes = [
            {"img": "scene_01.jpg", "start": 0.00,  "end": 5.50,  "motion": "zoom_in"},
            {"img": "scene_02.jpg", "start": 5.50,  "end": 10.70, "motion": "pan_up"},
            {"img": "scene_03.jpg", "start": 10.70, "end": 17.60, "motion": "dramatic_punch"},
            {"img": "scene_04.jpg", "start": 17.60, "end": 23.80, "motion": "pan_down"},
            {"img": "scene_05.jpg", "start": 23.80, "end": 29.60, "motion": "zoom_in"},
            {"img": "scene_06.jpg", "start": 29.60, "end": 36.60, "motion": "pan_up"},
            {"img": "scene_07.jpg", "start": 36.60, "end": 41.40, "motion": "zoom_in"},
            {"img": "scene_08.jpg", "start": 41.40, "end": 48.80, "motion": "dramatic_punch"},
            {"img": "scene_09.jpg", "start": 48.80, "end": 53.80, "motion": "pan_up"},
            {"img": "scene_10.jpg", "start": 53.80, "end": 56.50, "motion": "zoom_out"},
            {"img": "scene_11.jpg", "start": 56.50, "end": total_duration, "motion": "zoom_in"}
        ]
        dialogues = [
            {"start": 0.00,  "end": 3.00,  "text": "IN 1974, A MAN WALKED OUT OF THE JUNGLE...", "style": "Default"},
            {"start": 3.00,  "end": 5.50,  "text": "AFTER BEING MISSING FOR 29 YEARS!", "style": "Accent"},
            {"start": 5.50,  "end": 7.80,  "text": "HIS NAME WAS HIROO ONODA.", "style": "Default"},
            {"start": 7.80,  "end": 10.70, "text": "IN 1944, HE RECEIVED ONE ORDER: NEVER SURRENDER.", "style": "Accent"},
            {"start": 10.70, "end": 13.50, "text": "THEN WORLD WAR II ENDED. JAPAN LOST.", "style": "Default"},
            {"start": 13.50, "end": 17.60, "text": "BUT ONODA BELIEVED IT WAS ENEMY PROPAGANDA!", "style": "Accent"},
            {"start": 17.60, "end": 20.80, "text": "FOR DECADES, HE HID IN THE DENSE JUNGLE...", "style": "Default"},
            {"start": 20.80, "end": 23.80, "text": "SURVIVING ON BANANAS, COCONUTS & STOLEN RICE.", "style": "Default"},
            {"start": 23.80, "end": 27.00, "text": "LEAFLETS WERE DROPPED FROM PLANES...", "style": "Default"},
            {"start": 27.00, "end": 29.60, "text": "HIS OWN FAMILY SENT LETTERS & RECORDINGS!", "style": "Default"},
            {"start": 29.60, "end": 33.00, "text": "HE REFUSED TO BELIEVE ANY OF THEM.", "style": "Accent"},
            {"start": 33.00, "end": 36.60, "text": "HIS COMPANIONS DIED OR SURRENDERED...", "style": "Default"},
            {"start": 36.60, "end": 41.40, "text": "UNTIL ONODA WAS ALONE, STILL FIGHTING HIS PRIVATE WAR!", "style": "Accent"},
            {"start": 41.40, "end": 45.20, "text": "UNTIL 1974, WHEN A TRAVELER TRACKED HIM DOWN.", "style": "Default"},
            {"start": 45.20, "end": 48.80, "text": "ONODA DEMANDED PROOF THE WAR WAS OVER!", "style": "Accent"},
            {"start": 48.80, "end": 51.50, "text": "JAPAN FLEW HIS FORMER COMMANDER TO THE ISLAND...", "style": "Default"},
            {"start": 51.50, "end": 53.80, "text": "YOU ARE RELIEVED OF YOUR DUTIES.", "style": "Accent"},
            {"start": 53.80, "end": 56.50, "text": "AFTER 29 YEARS, HE FINALLY LAID DOWN HIS SWORD.", "style": "Default"},
            {"start": 56.50, "end": total_duration, "text": "THE WAR HAD ENDED BEFORE HE EVEN KNEW IT.", "style": "Accent"}
        ]
    elif "nalanda" in video_id:
        scenes = [
            {"img": "scene_01.jpg", "start": 0.00,  "end": 5.50,  "motion": "zoom_in"},
            {"img": "scene_02.jpg", "start": 5.50,  "end": 11.00, "motion": "pan_up"},
            {"img": "scene_05.jpg", "start": 11.00, "end": 16.50, "motion": "zoom_in"},
            {"img": "scene_04.jpg", "start": 16.50, "end": 22.00, "motion": "pan_up"},
            {"img": "scene_03.jpg", "start": 22.00, "end": 28.50, "motion": "zoom_out"},
            {"img": "scene_06.jpg", "start": 28.50, "end": 34.50, "motion": "dramatic_punch"},
            {"img": "scene_07.jpg", "start": 34.50, "end": 39.80, "motion": "zoom_in"},
            {"img": "scene_08.jpg", "start": 39.80, "end": 43.50, "motion": "pan_down"},
            {"img": "scene_09.jpg", "start": 43.50, "end": total_duration, "motion": "zoom_in"}
        ]
        dialogues = [
            {"start": 0.00,  "end": 3.00,  "text": "MORE THAN A THOUSAND YEARS AGO...", "style": "Default"},
            {"start": 3.00,  "end": 5.50,  "text": "STUDENTS TRAVELED ACROSS ASIA TO INDIA!", "style": "Accent"},
            {"start": 5.50,  "end": 7.50,  "text": "IT WAS CALLED NALANDA.", "style": "Accent"},
            {"start": 7.50,  "end": 11.00, "text": "ONE OF THE WORLD'S GREATEST CENTERS OF LEARNING.", "style": "Default"},
            {"start": 11.00, "end": 13.80, "text": "THEY STUDIED PHILOSOPHY, LOGIC, MEDICINE & GRAMMAR...", "style": "Default"},
            {"start": 13.80, "end": 16.50, "text": "WRITTEN ON SACRED ANCIENT TEXTS.", "style": "Default"},
            {"start": 16.50, "end": 19.20, "text": "CHINESE SCHOLARS LIKE XUANZANG...", "style": "Default"},
            {"start": 19.20, "end": 22.00, "text": "TRAVELED THOUSANDS OF MILES TO BE HERE!", "style": "Accent"},
            {"start": 22.00, "end": 25.20, "text": "IMAGINE SCHOLARS FROM DIFFERENT REGIONS...", "style": "Default"},
            {"start": 25.20, "end": 28.50, "text": "GATHERED TO DEBATE AND EXCHANGE IDEAS.", "style": "Default"},
            {"start": 28.50, "end": 31.50, "text": "BUT NALANDA'S HISTORY INCLUDES DESTRUCTION.", "style": "Default"},
            {"start": 31.50, "end": 34.50, "text": "IN THE LATE 12TH CENTURY, IT WAS ATTACKED.", "style": "Accent"},
            {"start": 34.50, "end": 39.80, "text": "ITS LEGENDARY LIBRARIES SUFFERED DEVASTATING DAMAGE.", "style": "Accent"},
            {"start": 39.80, "end": 43.50, "text": "TODAY, ITS RUINS REMAIN IN BIHAR...", "style": "Default"},
            {"start": 43.50, "end": total_duration, "text": "ATTRACTING THE WORLD CENTURIES BEFORE MODERN UNIVERSITIES!", "style": "Accent"}
        ]
    elif video_id == "the-day-cavemen-discovered-fire":
        scenes = [
            {"img": "scene_01.jpg", "start": 0.00,  "end": 5.10,  "motion": "zoom_in"},
            {"img": "scene_02.jpg", "start": 5.10,  "end": 9.20,  "motion": "dramatic_punch"},
            {"img": "scene_03.jpg", "start": 9.20,  "end": 14.80, "motion": "zoom_in"},
            {"img": "scene_04.jpg", "start": 14.80, "end": 20.80, "motion": "pan_up"},
            {"img": "scene_05.jpg", "start": 20.80, "end": total_duration, "motion": "zoom_out"}
        ]
        dialogues = [
            {"start": 0.00,  "end": 2.50,  "text": "50,000 YEARS AGO...", "style": "Default"},
            {"start": 2.50,  "end": 5.00,  "text": "HUMANS WERE ONE STEP FROM BEING ICE POPS!", "style": "Accent"},
            {"start": 5.10,  "end": 7.30,  "text": "UNTIL NATURE DROPPED A LIGHTNING BOLT...", "style": "Default"},
            {"start": 7.30,  "end": 9.10,  "text": "RIGHT INTO A DEAD TREE!", "style": "Accent"},
            {"start": 9.20,  "end": 11.20, "text": "DID OUR BOY RUN AWAY? NOPE!", "style": "Default"},
            {"start": 11.20, "end": 14.70, "text": "HE SPRINTED WITH A FLAMING TORCH!", "style": "Accent"},
            {"start": 14.80, "end": 17.50, "text": "AND THE FOOD CHAIN WAS OFFICIALLY FLIPPED.", "style": "Default"},
            {"start": 17.50, "end": 20.70, "text": "PREDATORS NOW CHECK UNDER THE BED FOR US!", "style": "Accent"},
            {"start": 20.80, "end": total_duration, "text": "WELCOME TO THE DAWN OF HUMANITY.", "style": "Accent"}
        ]
    else:
        scenes = [
            {"img": "scene_01.jpg", "start": 0.00,  "end": 2.60,  "motion": "dramatic_punch"},
            {"img": "scene_02.jpg", "start": 2.60,  "end": 6.30,  "motion": "pan_up"},
            {"img": "scene_03.jpg", "start": 6.30,  "end": 10.40, "motion": "zoom_in"},
            {"img": "scene_04.jpg", "start": 10.40, "end": 16.00, "motion": "zoom_in"},
            {"img": "scene_05.jpg", "start": 16.00, "end": 18.60, "motion": "dramatic_punch"},
            {"img": "scene_06.jpg", "start": 18.60, "end": 24.20, "motion": "zoom_in"},
            {"img": "scene_07.jpg", "start": 24.20, "end": 27.60, "motion": "pan_up"},
            {"img": "scene_08.jpg", "start": 27.60, "end": 30.50, "motion": "pan_down"},
            {"img": "scene_09.jpg", "start": 30.50, "end": 32.20, "motion": "pan_down"},
            {"img": "scene_10.jpg", "start": 32.20, "end": 35.00, "motion": "zoom_out"},
            {"img": "scene_11.jpg", "start": 35.00, "end": total_duration, "motion": "zoom_in"}
        ]
        dialogues = [
            {"start": 0.00,  "end": 2.50,  "text": "THINK HUNTING A WOOLLY MAMMOTH WAS EASY?", "style": "Default"},
            {"start": 2.60,  "end": 4.50,  "text": "THESE BEASTS WERE FOUR METERS TALL...", "style": "Default"},
            {"start": 4.50,  "end": 6.20,  "text": "WITH RAZOR SHARP TUSKS!", "style": "Accent"},
            {"start": 6.30,  "end": 8.50,  "text": "A DIRECT SPEAR THROW?", "style": "Default"},
            {"start": 8.50,  "end": 10.30, "text": "THAT WOULD JUST TICKLE IT AND MAKE IT FURIOUS!", "style": "Accent"},
            {"start": 10.40, "end": 13.20, "text": "SO CAVEMEN SPENT DAYS DIGGING MASSIVE PIT TRAPS...", "style": "Default"},
            {"start": 13.20, "end": 15.90, "text": "IN THE FREEZING PERMAFROST!", "style": "Default"},
            {"start": 16.00, "end": 18.50, "text": "THEN CAME THE CRAZIEST JOB IN HISTORY: THE HUMAN BAIT!", "style": "Accent"},
            {"start": 18.60, "end": 21.50, "text": "CHARGING THROUGH THE SNOW...", "style": "Default"},
            {"start": 21.50, "end": 24.10, "text": "WITH A SEVEN-TON MONSTER ON HIS TAIL!", "style": "Accent"},
            {"start": 24.20, "end": 27.50, "text": "AT THE LAST SECOND, OUR BOY LEAPS ACROSS!", "style": "Default"},
            {"start": 27.60, "end": 28.70, "text": "CRASH!!", "style": "Accent"},
            {"start": 28.70, "end": 30.40, "text": "THE MAMMOTH PLUNGES RIGHT IN!", "style": "Default"},
            {"start": 30.50, "end": 32.10, "text": "THE TRIBE SWARMS FROM THE RIDGES!", "style": "Default"},
            {"start": 32.20, "end": 34.90, "text": "SECURING FOOD FOR THREE WHOLE MONTHS!", "style": "Accent"},
            {"start": 35.00, "end": total_duration, "text": "TEAMWORK & BIG HOLES MADE US KINGS OF THE ICE AGE!", "style": "Accent"},
        ]

    print("\n--- 1. Rendering Motion Clips ---")
    clip_paths = []
    for i, sc in enumerate(scenes, 1):
        img_file = images_dir / sc["img"]
        duration = sc["end"] - sc["start"]
        clip_out = temp_dir / f"clip_{i:02d}.mp4"
        print(f"  Rendering Scene {i:02d} ({duration:.2f}s, {sc['motion']})...")
        render_scene_clip(img_file, duration, clip_out, motion_type=sc["motion"])
        clip_paths.append(clip_out)

    concat_list_file = temp_dir / "concat_list.txt"
    with open(concat_list_file, "w") as f:
        for p in clip_paths:
            f.write(f"file '{p.absolute()}'\n")

    raw_video = temp_dir / "raw_video.mp4"
    print("\n--- 2. Concatenating Scene Clips ---")
    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list_file),
        "-c", "copy",
        str(raw_video)
    ]
    subprocess.run(concat_cmd, check=True, stdout=subprocess.DEVNULL)

    print("\n--- 3. Generating Styled ASS Subtitles ---")
    ass_file = temp_dir / "subtitles.ass"
    generate_ass_subtitles(dialogues, ass_file)

    print("\n--- 4. Final Compositing (Audio + Subtitles) ---")
    final_output = out_dir / f"{video_id}_final.mp4"
    
    merge_cmd = [
        "ffmpeg", "-y",
        "-i", str(raw_video),
        "-i", str(audio_path),
        "-vf", f"ass={ass_file}",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(final_output)
    ]
    subprocess.run(merge_cmd, check=True)

    print(f"\n🎉 Video Successfully Generated!")
    print(f"Output: {final_output}")
    print(f"Resolution: 1080x1920 (9:16 Vertical)")
    print(f"Duration: {total_duration:.2f}s")
    return str(final_output)

if __name__ == "__main__":
    vid = sys.argv[1] if len(sys.argv) > 1 else None
    build_short_video(vid)
