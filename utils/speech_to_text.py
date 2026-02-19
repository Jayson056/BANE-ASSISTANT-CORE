
import speech_recognition as sr
from pydub import AudioSegment
import os
import sys

def transcribe_audio(file_path):
    """
    Transcribes an audio file (ogg, mp3, wav, etc.) to text using Google Web Speech API.
    """
    if not os.path.exists(file_path):
        return None, f"File not found: {file_path}"

    ext = os.path.splitext(file_path)[1].lower()
    temp_wav = "/home/user/BANE_CORE/storage/temp_transcription.wav"

    try:
        # Convert to WAV (required by SpeechRecognition)
        if ext == '.ogg':
            audio = AudioSegment.from_ogg(file_path)
            audio.export(temp_wav, format="wav")
        elif ext == '.mp3':
            audio = AudioSegment.from_mp3(file_path)
            audio.export(temp_wav, format="wav")
        elif ext == '.wav':
            temp_wav = file_path # Already WAV
        else:
            # Try generic load
            audio = AudioSegment.from_file(file_path)
            audio.export(temp_wav, format="wav")

        # Initialize recognizer
        r = sr.Recognizer()
        with sr.AudioFile(temp_wav) as source:
            audio_data = r.record(source)
            # Use Google Web Speech API (Free, no key needed for low volume)
            text = r.recognize_google(audio_data)
            
        # Cleanup temp file if we created one
        if temp_wav != file_path and os.path.exists(temp_wav):
            os.remove(temp_wav)
            
        return text, None

    except sr.UnknownValueError:
        return None, "Speech was unintelligible"
    except sr.RequestError as e:
        return None, f"Could not request results from Google Speech Recognition service; {e}"
    except Exception as e:
        if os.path.exists(temp_wav) and temp_wav != file_path:
            os.remove(temp_wav)
        return None, str(e)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 speech_to_text.py <audio_file_path>")
        sys.exit(1)
    
    result, error = transcribe_audio(sys.argv[1])
    if result:
        print(result)
        sys.exit(0)
    else:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
