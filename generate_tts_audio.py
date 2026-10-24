import os
import wave
import re
import pathlib
from google import genai
from google.genai import types

def generate():
    # 1. Setup paths and read the generated emotion script
    script_dir = pathlib.Path(__file__).parent.absolute()
    topics_file = script_dir / "channel" / "topics.md"
    
    content = ""
    if topics_file.exists():
        content = topics_file.read_text(encoding="utf-8")
        
    latest_title = None
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("Title:"):
            latest_title = line[len("Title:"):].strip()
            
    if not latest_title:
        print("No topic found in topics.md")
        return None
        
    video_id = re.sub(r'[^a-z0-9]+', '-', latest_title.lower()).strip('-')
    emotion_script_file = script_dir / "videos" / video_id / "script" / "emotion_script.md"
    
    if not emotion_script_file.exists():
        print(f"Emotion script not found: {emotion_script_file}")
        return None
        
    transcript_text = emotion_script_file.read_text(encoding="utf-8")
    
    # Extract only the Narration part from emotion_script.md
    if "## Narration" in transcript_text:
        transcript_text = transcript_text.split("## Narration")[1].strip()
        # Remove QA section if it exists
        if "## Script QA" in transcript_text:
            transcript_text = transcript_text.split("## Script QA")[0].strip()
            
    # Clean up any leftover line breaks to guarantee a single seamless block for TTS
    transcript_text = " ".join(transcript_text.split())

    # 2. Start the Gemini Client with the valid API key
    api_key = os.environ.get("GEMINI_API_KEY")
    # If the environment variable isn't an AIza key or fails, fall back to the provided functional key
    default_key = "AIzaSyDStjE_IOWgo7NWUSqrxHi3KBki2Rfyk0k"
    if not api_key or not api_key.startswith("AIza"):
        api_key = default_key

    client = genai.Client(api_key=api_key)
    model = "gemini-3.1-flash-tts-preview"
    
    # 3. The New Script and Context
    prompt_content = f"""Read the following transcript based on the audio profile and director's note.

# Audio Profile
A young, casual YouTube storyteller. The voice is completely effortless, slightly dry, and relaxed. Zero pressure, no dramatic acting, just a smooth, natural speaking voice.

# Director's note
Style: Flat affect, minimal pitch variation, dry delivery. Pace: Fast, energetic, no dead air. Sentences overlap slightly. Accent: American (General).

## Scene:
A casual bedroom studio. A young guy is calmly explaining a cool history topic to his audience with a relaxed, dry delivery.

## Sample Context:
Smooth, modern YouTube essay style. The delivery is extremely casual, flat, and effortless. The speaker drops all theatrical pressure and just talks normally, like a real person having a calm conversation.

## Transcript:
{transcript_text}"""

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt_content)],
        ),
    ]
    
    # 4. Apply the Voice (Achird - the smooth casual narrator)
    generate_content_config = types.GenerateContentConfig(
        temperature=0.9,
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Achird"
                )
            )
        ),
    )

    print(f"Connecting to Gemini and generating audio for: {latest_title}...")
    
    # 5. Request the single audio file
    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
    except Exception as e:
        print(f"Primary API key attempt failed: {e}. Retrying with fallback key...")
        client = genai.Client(api_key=default_key)
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )

    # 6. Save the audio
    try:
        if not response.candidates:
            print("Error: No candidates in response.")
            print("Response:", response)
            return None

        part = response.candidates[0].content.parts[0]
        if part.inline_data and part.inline_data.data:
            raw_audio = part.inline_data.data
            
            # Create the audio output directory if it doesn't exist
            audio_dir = script_dir / "audio"
            audio_dir.mkdir(parents=True, exist_ok=True)
            
            # Name the file and save it to the audio folder
            output_filename = audio_dir / f"{video_id}.wav"
            
            # Format the sound so it plays instantly on macOS/Windows
            with wave.open(str(output_filename), "wb") as wav_file:
                wav_file.setnchannels(1)       # Mono sound
                wav_file.setsampwidth(2)       # 16-bit audio depth
                wav_file.setframerate(24000)   # 24kHz studio speed
                wav_file.writeframes(raw_audio)
                
            # Get duration
            frames = len(raw_audio) // 2
            duration_sec = frames / 24000.0
            print(f"\nSuccess! Your audio is saved as: {output_filename}")
            print(f"Audio Duration: {duration_sec:.2f} seconds")
            return {
                "video_id": video_id,
                "audio_path": str(output_filename),
                "duration": duration_sec,
                "narration": transcript_text
            }
        else:
            print("No audio data returned from the model.")
            return None
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"An error occurred while building the file: {e}")
        return None

if __name__ == "__main__":
    generate()
