import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

# Load env
load_dotenv("/home/user/BANE_CORE/config/secrets.env")
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

def analyze_video(video_path):
    print(f"Uploading file: {video_path}...")
    video_file = genai.upload_file(path=video_path)
    print(f"Completed upload: {video_file.uri}")

    # Check for processing
    while video_file.state.name == "PROCESSING":
        print('.', end='', flush=True)
        time.sleep(5)
        video_file = genai.get_file(video_file.name)

    if video_file.state.name == "FAILED":
        raise Exception(video_file.state.name)

    print("\nAnalyzing video...")
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
    response = model.generate_content([video_file, "Summarize the observation or recommendation mentioned in this video. The video is from an admin monitoring an AI system."])
    
    print("\n--- ANALYSIS RESULT ---")
    print(response.text)
    
    # Clean up file in cloud
    genai.delete_file(video_file.name)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python analyze_video.py <video_path>")
        sys.exit(1)
    
    analyze_video(sys.argv[1])
