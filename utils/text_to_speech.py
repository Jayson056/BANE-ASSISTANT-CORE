# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import sys
import os
import time
from gtts import gTTS

# ── Telegram Bot API Limits ──
# sendVoice: max 50MB, must be OGG with OPUS codec for native voice bubble
# sendAudio: max 50MB, supports MP3/M4A
# Safe target: keep voice files under 1MB for fast delivery
# ── Voice Personas (gTTS based) ──
VOICE_MODELS = {
    "nova": {"lang": "en", "tld": "com", "speed": False},     # Standard US (Neutral)
    "atlas": {"lang": "en", "tld": "co.uk", "speed": False}, # British (Professional/Serious)
    "sage": {"lang": "en", "tld": "com.au", "speed": False},  # Australian (Casual/Natural)
    "echo": {"lang": "en", "tld": "ca", "speed": True},       # Canadian (Slow/Methodical)
    "default": {"lang": "en", "tld": "com", "speed": False}
}

MAX_VOICE_SIZE_BYTES = 50 * 1024 * 1024  # 50MB absolute max
WARN_SIZE_BYTES = 1 * 1024 * 1024        # 1MB soft warning threshold

def detect_voice_config(text):
    """
    Intelligently detects language/accent based on anchor words.
    Returns: (lang, tld)
    """
    text = text.lower()
    
    # 1. Non-Latin scripts (Highest Confidence)
    if any('\u4e00' <= c <= '\u9fff' for c in text): return "zh-CN", "com"     # Chinese
    if any('\u3040' <= c <= '\u30ff' for c in text): return "ja", "com"        # Japanese
    if any('\uac00' <= c <= '\ud7a3' for c in text): return "ko", "com"        # Korean
    if any('\u0400' <= c <= '\u04ff' for c in text): return "ru", "com"        # Russian

    # 2. Tagalog / Filipino (Primary)
    tl_anchors = ["ako", "ikaw", "siya", "tayo", "kami", "salamat", "po", "opo", "mabuhay", "kamusta"]
    if any(word in text for word in tl_anchors): return "tl", "com"

    # 3. Western European Accents
    if any(word in text for word in ["bonjour", "merci", "salut"]): return "fr", "fr"      # French
    if any(word in text for word in ["hola", "gracias", "amigo"]): return "es", "es"       # Spanish
    if any(word in text for word in ["hallo", "danke", "tschüss"]): return "de", "de"     # German
    if any(word in text for word in ["ciao", "grazie", "prego"]): return "it", "it"       # Italian
    if any(word in text for word in ["olá", "obrigado", "bom"]): return "pt", "pt"        # Portuguese

    # Default to English (US)
    return "en", "com"

def _segment_polyglot(text):
    """
    Splits text into chunks by language script/anchors.
    Returns: list of (lang, tld, text)
    """
    import re
    # Simple strategy: split by common sentence punctuation or script changes
    # For now, we split by sentences/newlines and detect lang for each
    segments = []
    
    # Extract headers (to ignore)
    lines = text.split('\n')
    skip_headers = ["✅", "❌", "⚠️", "ℹ️", "🖥️", "⚙️", "🧠", "💾", "🔝", "🚀", "🛰️", "🦅", "📸", "🎥", "🛡️", "🔑", "📡", "📉"]
    
    for line in lines:
        # Pre-clean line for header detection (remove bold/italic symbols)
        clean_line = line.strip().replace("*", "").replace("_", "").replace("#", "")
        if not clean_line: continue
        
        # Detect headers by icons or ultra-short leading summary lines
        is_header = any(icon in clean_line[:3] for icon in skip_headers) and len(clean_line) < 100
        if is_header: continue
        
        # Split line into sub-segments by language block
        # We look for script boundaries: [Latin], [CJK], [Hangul]
        import re
        blocks = re.findall(r'[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]+|[^\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]+', line)
        
        for block in blocks:
            b_text = block.strip()
            if not b_text: continue
            lang, tld = detect_voice_config(b_text)
            segments.append((lang, tld, b_text))
            
    return segments

def text_to_mp3(text, output_file=None, retries=3, voice_id="default"):
    """Converts text to speech, supporting multi-language switching."""
    from pydub import AudioSegment
    import io
    
    storage_dir = "/home/son/BANE/storage"
    os.makedirs(storage_dir, exist_ok=True)
    
    if not output_file:
        timestamp = int(time.time())
        output_file = os.path.join(storage_dir, f"speech_{timestamp}.mp3")
    
    abs_output = os.path.abspath(output_file)
    
    # ── Polyglot Mode ──
    # If using default/auto, we check for multi-language segments
    if voice_id in ["default", "auto"]:
        segments = _segment_polyglot(text)
        if not segments: return False, "No speakable text detected"
        
        combined = AudioSegment.empty()
        
        for lang, tld, s_text in segments:
            # Clean segment for speech (remove formatting)
            s_clean = s_text.replace("*", "").replace("_", "").replace("`", "").replace("#", "").replace("-", " ")
            
            for attempt in range(retries):
                try:
                    tts = gTTS(text=s_clean, lang=lang, tld=tld)
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    fp.seek(0)
                    chunk = AudioSegment.from_file(fp, format="mp3")
                    combined += chunk
                    combined += AudioSegment.silent(duration=300)
                    break
                except Exception as e:
                    if attempt == retries - 1: return False, str(e)
                    time.sleep(1)
        
        # Final export
        combined.export(abs_output, format="mp3", parameters=["-ar", "24000", "-ac", "1"])
        return True, abs_output
        
    else:
        # Standard Persona Mode (Single Voice)
        voice_cfg = VOICE_MODELS.get(voice_id, VOICE_MODELS["default"])
        
        # Pre-process text: Filter out headers
        lines = text.split('\n')
        filtered = []
        skip_headers = ["✅", "❌", "⚠️", "ℹ️", "🖥️", "⚙️", "🧠", "💾", "🔝", "🚀", "🛰️", "🦅", "📸", "🎥", "🛡️", "🔑", "📡", "📉"]
        for l in lines:
            clean_l = l.strip().replace("*", "").replace("_", "").replace("#", "")
            if not clean_l: continue
            
            # Skip short lines that start with status icons (Headers)
            if any(icon in clean_l[:3] for icon in skip_headers) and len(clean_l) < 100:
                continue
            filtered.append(l)
        
        clean_text = "\n".join(filtered).replace("*","").replace("_","").replace("`","").replace("#","").replace("-"," ")
        
        for attempt in range(retries):
            try:
                tts = gTTS(text=clean_text.strip(), lang=voice_cfg["lang"], tld=voice_cfg["tld"], slow=voice_cfg["speed"])
                tts.save(abs_output)
                return True, abs_output
            except Exception as e:
                if attempt == retries - 1: return False, str(e)
                time.sleep(2)
        return False, "Unknown error"


def text_to_ogg(text, output_file=None, retries=3, voice_id="default"):
    """
    Converts text to Telegram-compliant OGG OPUS voice file using a specific voice persona.
    """
    storage_dir = "/home/son/BANE/storage"
    os.makedirs(storage_dir, exist_ok=True)
    
    if not output_file:
        timestamp = int(time.time())
        output_file = os.path.join(storage_dir, f"voice_{timestamp}.ogg")
    
    abs_output = os.path.abspath(output_file)
    
    # Step 1: Generate MP3 first
    temp_mp3 = abs_output.replace('.ogg', '_temp.mp3')
    success, result = text_to_mp3(text, temp_mp3, retries, voice_id=voice_id)
    
    if not success:
        return False, result
    
    # Step 2: Convert MP3 → OGG OPUS using ffmpeg
    try:
        import subprocess
        cmd = [
            'ffmpeg', '-y',
            '-i', temp_mp3,
            '-c:a', 'libopus',       # Opus codec (Telegram standard)
            '-b:a', '32k',           # 32kbps — excellent for speech, very small files
            '-vbr', 'on',            # Variable bitrate for speech efficiency
            '-application', 'voip',  # Optimized for voice
            '-ar', '24000',          # 24kHz sample rate (sufficient for speech)
            '-ac', '1',              # Mono (voice doesn't need stereo)
            abs_output
        ]
        
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        # Cleanup temp MP3
        if os.path.exists(temp_mp3):
            os.remove(temp_mp3)
        
        if proc.returncode != 0:
            return False, f"FFmpeg error: {proc.stderr[:200]}"
        
        # Verify size
        file_size = os.path.getsize(abs_output)
        if file_size > MAX_VOICE_SIZE_BYTES:
            os.remove(abs_output)
            return False, f"Voice file too large ({file_size // 1024}KB). Telegram limit is 50MB."
        
        if file_size > WARN_SIZE_BYTES:
            print(f"⚠️ Voice file is {file_size // 1024}KB — consider shorter text for faster delivery.")
        
        return True, abs_output
        
    except FileNotFoundError:
        # ffmpeg not available, fallback to MP3
        print("⚠️ ffmpeg not found. Falling back to MP3 format.")
        # Rename temp back
        if os.path.exists(temp_mp3):
            mp3_fallback = abs_output.replace('.ogg', '.mp3')
            os.rename(temp_mp3, mp3_fallback)
            return True, mp3_fallback
        return False, "ffmpeg not found and temp file missing"
    except Exception as e:
        if os.path.exists(temp_mp3):
            os.remove(temp_mp3)
        return False, str(e)


def cleanup_old_speech_files(max_age_hours=24, max_files=50):
    """Remove old speech/voice files to prevent storage bloat."""
    storage_dir = "/home/son/BANE/storage"
    if not os.path.exists(storage_dir):
        return
    
    now = time.time()
    speech_files = []
    
    for f in os.listdir(storage_dir):
        if f.startswith(("speech_", "voice_")) and f.endswith((".mp3", ".ogg")):
            fpath = os.path.join(storage_dir, f)
            age_hours = (now - os.path.getmtime(fpath)) / 3600
            speech_files.append((fpath, age_hours))
    
    # Sort by age (oldest first)
    speech_files.sort(key=lambda x: x[1], reverse=True)
    
    removed = 0
    for fpath, age in speech_files:
        # Remove if older than max_age_hours OR if we have too many files
        if age > max_age_hours or (len(speech_files) - removed) > max_files:
            try:
                os.remove(fpath)
                removed += 1
            except Exception:
                pass
    
    if removed > 0:
        print(f"🧹 Cleaned up {removed} old speech files.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 text_to_speech.py \"Text to speak\" [output_file]")
        print("  python3 text_to_speech.py --ogg \"Text to speak\" [output_file] [--voice nova|atlas|sage|echo]")
        print("  python3 text_to_speech.py --cleanup")
        sys.exit(1)
    
    # Handle cleanup command
    if sys.argv[1] == "--cleanup":
        cleanup_old_speech_files()
        sys.exit(0)
    
    # Standard arg parsing for voice model
    voice_id = "default"
    if "--voice" in sys.argv:
        v_idx = sys.argv.index("--voice")
        if v_idx + 1 < len(sys.argv):
            voice_id = sys.argv[v_idx + 1]
            # Remove from argv to avoid confusion
            sys.argv.pop(v_idx + 1)
            sys.argv.pop(v_idx)
    
    # Handle OGG mode (preferred for Telegram)
    if sys.argv[1] == "--ogg":
        if len(sys.argv) < 3:
            print("Error: No text provided for --ogg mode")
            sys.exit(1)
        text = sys.argv[2]
        output = sys.argv[3] if len(sys.argv) > 3 else None
        success, result = text_to_ogg(text, output, voice_id=voice_id)
    else:
        text = sys.argv[1]
        output = sys.argv[2] if len(sys.argv) > 2 else None
        success, result = text_to_mp3(text, output, voice_id=voice_id)
    
    if success:
        print(result)
        sys.exit(0)
    else:
        print(f"❌ Error: {result}")
        sys.exit(1)
