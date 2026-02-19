# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
"""
Response Capture Module for Antigravity.

Captures the AI's text response from the Antigravity UI via OCR,
then generates a voice version and sends both text + voice to Telegram.

This implements the "Dual-Mode" feature:
  Every AI response includes Text + Voice
"""
import logging
import os
import time

logger = logging.getLogger(__name__)

# Noise lines to filter out of OCR output (UI elements, not response text)
UI_NOISE = [
    "antigravity", "accept all", "reject all", "file", "edit", "view",
    "terminal", "help", "run", "debug", "extensions", "search",
    "source control", "explorer", "problems", "output", "debug console",
    "ports", "comments", "ask", "type a message", "gemini",
    "thinking", "generating", "loading", "progress",
    "send", "cancel", "chat", "copilot", "new chat",
    "breadcrumb", "minimap", "scrollbar", "status bar", "activity bar", "side bar", "panel", "editor",
    "final_text", "v_path", "python3", "bash", "echo", "nohup",
    "scripts/", "utils/", "bin/python", "cd /home/son",
    "stdout", "stderr", "exit code", "log", "nohup.out",
    "son@son", "~/", "bash-", "sh-", "root@",
    "summary:", "step id:", "enc[", "enciaes",
    # Sidebar Artifacts
    "bane", "utils", "scripts", "core", "antigravity", "logs", "docs", "storage",
    "timeline", "outline", "search", "explorer", "source control", "extensions",
    # Agent UI Header Artifacts
    "switch to agent manager", "code with agent", "open agent manager", "dogs ge",
    "restoring telegram", "messenger", "active skill", "persona:", "skill_file:",
    "mandatory:", "you answer/respond", "send via", "platform messenger",
    "ask anything", "@ to mention", "ctrl", "+", "history", "context",
    "enc{", "aes256", "test again", "teste", "woh", "onhing", "ihsk", "mer", "seen"
]

# Minimum length to consider as a valid AI response line
MIN_LINE_LENGTH = 1

# Max chars to send as voice (voice gets truncated beyond this)
MAX_VOICE_CHARS = 3000


def capture_response_text():
    """
    Capture the latest AI response from Antigravity's visible UI.
    Uses optimized OCR cropped to the active window.
    
    Returns:
        str: The cleaned response text, or None if capture failed.
    """
    try:
        from utils.ocr_helper import run_optimized_ocr
        
        # We use a higher scale (0.8) for final capture to ensure 
        # text legibility and markdown/emoji preservation.
        # Exclude left 22% (Sidebar) and bottom 35% (Input Bar + Terminal)
        raw_text = run_optimized_ocr(crop_to_window=True, downscale=0.8, exclude_left_percent=0.22, exclude_bottom_percent=0.35)

        if not raw_text or len(raw_text.strip()) < 10:
            logger.warning("OCR returned too little text to extract a response.")
            return None

        # Clean and filter
        lines = raw_text.split('\n')
        response_lines = []
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            # Skip lines that are clearly UI elements or system noise
            lower = stripped.lower()
            if any(noise in lower for noise in UI_NOISE):
                continue
            
            # Regex to filter out terminal prompts (e.g. "son@son:~/BANE$")
            import re
            if re.search(r'[\w-]+@[\w-]+:.*[\$#]', stripped):
                continue

            # Filter out timestamps (e.g. 2026-02-18 22:22:...)
            if re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}', stripped):
                continue
                
            # Filter out file paths (e.g. /home/son/...)
            if stripped.startswith("/") or stripped.startswith("~"):
                continue

            # Filter out System Context Tags: [CTX|...], [META|...], [SYSTEM|...]
            if re.search(r'\[(CTX|META|SYSTEM|U:|P:|S:).*\]', stripped, re.IGNORECASE):
                continue

            # Relaxed Filter: Allow short responses (e.g. "Ok", "Done")
            if len(stripped) > 5:
                alpha_ratio = sum(c.isalpha() for c in stripped) / max(len(stripped), 1)
                # If it's mostly random symbols/numbers and not much text, ignore it
                if alpha_ratio < 0.15: 
                    continue
            
            response_lines.append(stripped)

        if not response_lines:
            logger.warning("No response lines extracted after filtering.")
            return None

        # Join and return the response text
        response_text = '\n'.join(response_lines)
        
        # Trim if extremely long (OCR might capture everything on screen)
        if len(response_text) > 5000:
            response_text = response_text[:5000] + "\n\n[Response truncated]"

        logger.info(f"Captured response: {len(response_text)} chars, {len(response_lines)} lines")
        return response_text

    except Exception as e:
        logger.error(f"Response capture failed: {e}")
        return None


async def send_response_with_voice(update, response_text):
    """
    Send the AI response as both text and voice via Telegram.
    
    Args:
        update: Telegram Update object
        response_text: The response text to send
    """
    if not response_text or len(response_text.strip()) < 10:
        return

    # Check for Group Chat context to suppress voice
    chat_type = update.effective_chat.type if update and update.effective_chat else None
    is_group = str(chat_type) in ['group', 'supergroup', 'ChatType.GROUP', 'ChatType.SUPERGROUP']

    # 1. Send text response
    try:
        # Split into chunks if necessary (Telegram 4096 char limit)
        text_chunks = _split_text(response_text, 4000)
        for chunk in text_chunks:
            try:
                await update.message.reply_markdown(f"🤖 **AI Response:**\n\n{chunk}")
            except Exception:
                # Fallback to plain text if markdown fails
                await update.message.reply_text(f"🤖 AI Response:\n\n{chunk}")
    except Exception as e:
        logger.error(f"Failed to send text response: {e}")

    # 2. Generate and send voice (SKIP FOR GROUPS)
    if is_group:
        logger.info("Skipping voice generation for Group Chat (Text-Only Mode active)")
        return

    try:
        voice_text = response_text[:MAX_VOICE_CHARS] if len(response_text) > MAX_VOICE_CHARS else response_text
        
        from utils.text_to_speech import text_to_ogg
        success, voice_path = text_to_ogg(voice_text)
        
        if success and os.path.exists(voice_path):
            file_size_kb = os.path.getsize(voice_path) // 1024
            logger.info(f"Voice generated: {voice_path} ({file_size_kb}KB)")
            
            try:
                with open(voice_path, 'rb') as voice_file:
                    await update.message.reply_voice(voice=voice_file)
                logger.info("Voice message sent successfully")
            except Exception as e:
                logger.error(f"Failed to send voice via Telegram: {e}")
                # Fallback: try sending as document
                try:
                    with open(voice_path, 'rb') as voice_file:
                        await update.message.reply_document(document=voice_file, filename="response.ogg")
                except Exception:
                    pass
            
            # Cleanup
            try:
                os.remove(voice_path)
            except Exception:
                pass
        else:
            logger.warning(f"Voice generation failed: {voice_path if not success else 'unknown error'}")
    except ImportError:
        logger.error("text_to_speech module not available for voice generation")
    except Exception as e:
        logger.error(f"Voice pipeline error: {e}")


def _split_text(text, max_length):
    """Split text into chunks of max_length, trying to break at line boundaries."""
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    while text:
        if len(text) <= max_length:
            chunks.append(text)
            break
        
        # Find a good break point
        break_at = text.rfind('\n', 0, max_length)
        if break_at == -1 or break_at < max_length // 2:
            break_at = text.rfind(' ', 0, max_length)
        if break_at == -1:
            break_at = max_length
        
        chunks.append(text[:break_at])
        text = text[break_at:].lstrip()
    
    return chunks
