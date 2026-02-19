
import requests
import sys
import subprocess
import os

def shorten_url(url):
    try:
        # Use TinyURL API
        api_url = f"http://tinyurl.com/api-create.php?url={url}"
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Error shortening URL: {e}")
    return None

def main():
    original_url = "https://jaysonmyportfolio-io.onrender.com/"
    short_url = shorten_url(original_url)
    
    if not short_url:
        print("Failed to shorten URL.")
        sys.exit(1)
        
    admin_chat_id = "5662168844"
    text = f"✅ **URL SHORTENED**\n\nOriginal: {original_url}\nShort Link: {short_url}"
    
    # Use send_telegram.py to reply to admin
    python_path = "/home/user/BANE_CORE/.venv/bin/python3"
    send_script = "/home/user/BANE_CORE/utils/send_telegram.py"
    
    try:
        subprocess.run([python_path, send_script, text, "--chat_id", admin_chat_id, "--title", "LINK SHORTENER"], check=True)
        print(f"Shortened link sent: {short_url}")
    except Exception as e:
        print(f"Error sending message: {e}")

if __name__ == "__main__":
    main()
