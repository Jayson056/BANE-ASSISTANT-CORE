# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import logging
import os
import asyncio
import json
import re
from datetime import datetime

# Telegram Imports
from telegram import Update, constants
from telegram.ext import ContextTypes
from telegram_interface.auth import is_authorized, is_admin_context
from telegram_interface.ui import accept_reject_keyboard

# Antigravity Imports
from antigravity.injector import send_to_antigravity
from antigravity.monitor import detect_state, get_error_details
from antigravity.button_mapper import detect_action_buttons

# Messenger Imports
from utils.message_history import save_message, get_message
from core import cortex_recall
from antigravity.shadow_encryptor import decrypt_text, set_shadow_state, is_shadow_active, encrypt_text

logger = logging.getLogger(__name__)

SCREENSHOTS_DIR = "storage/screenshots"
VOICE_ENABLED = True

class UniversalProcessor:
    """
    Handles AI injection logic for all platforms (Telegram, Messenger).
    Abstracts transport layers (Updates/Payloads) into a unified pipeline.
    """

    @staticmethod
    async def process_request(
        platform: str,
        user_id: str,
        chat_id: str,
        message_text: str,
        attachments: list,
        reply_context: str,
        role: str,
        user_paths: dict,
        send_reply: callable,
        send_buttons: callable = None,
        context_data: dict = None
    ):
        """
        Generic processing pipeline:
        1. Context Construction
        2. Concurrency Check
        3. Dashboard Sync
        4. Injection to Antigravity
        5. Wait Loop & Response Detection
        """
        
        # 1. Platform Acknowledgment (Immediate feedback handled at entry point)
        is_private = context_data.get("is_private", True) if context_data else True
        
        # 2. Concurrency Management
        state = detect_state()
        if state == "busy":
            if is_private:
                await send_reply("⚠️ **SYSTEM BUSY**\n\nThe AI is currently processing another request. Please wait.")
            return

        # 3. Dashboard Sync & Persistent History (Handled in background)
        try:
            from utils.logger import log_conversation_step
            log_text = message_text
            if attachments:
                log_text += f"\n[ATTACHMENTS: {', '.join([os.path.basename(a['path']) for a in attachments])}]"
            log_conversation_step(log_text, "user", user_id=user_id)
        except:
            pass

        # 4. Auto-Sort Attachments (School Organization)
        if attachments and user_paths.get('workspace'):
            sort_results = UniversalProcessor._auto_sort_attachments(user_id, user_paths, attachments)
            if sort_results:
                await send_reply(f"📁 **Auto-Sorted Attachments:**\n{sort_results}")

        # 3. Synchronize to Dashboard (Background - Latency Saver)
        asyncio.create_task(asyncio.to_thread(UniversalProcessor._sync_to_dashboard, user_id, message_text, attachments))

        # 5. Construct Injection Payload (BANE v2 compressed)
        shadow_on = is_shadow_active()
        user_hash = user_paths.get('hash', '?')
        # Compressed: U=User, P=Platform, S=Shadow
        compressed_ctx = f"[CTX|U:{user_id}|P:{platform}|S:{'ON' if shadow_on else 'OFF'}]"
        
        # 6. Full Injection Pipeline
        # Build message body (attachments INSIDE CTX tags so injector captures them)
        message_body = f"{message_text}{reply_context}"
        if attachments:
            for att in attachments:
                message_body += f"\n📎 **ATTACHED {att['type'].upper()}:** Path: `{att['path']}`"
        full_message = f"{compressed_ctx}\n{message_body}\n{compressed_ctx}"

        # 7. CORTEX QUOTA GUARD (Proactive Bypass)
        quota_cfg = cortex_recall.get_degradation_config()
        if not quota_cfg["use_ai"] or role == "guest":
            q_fallback = cortex_recall.handle_quota_mode(user_hash, message_text, bool(attachments))
            if q_fallback and q_fallback.get("confidence", 0) > 0.8:
                await send_reply(q_fallback["text"])
                return

        logger.info(f"Injecting message from {platform.upper()} User {user_id}")

        # 8. Inject to Antigravity
        success, status = await asyncio.to_thread(send_to_antigravity, full_message)

        if success:
            await asyncio.sleep(1.5)
            # 9. Enter Wait Loop & Capturing Response
            await UniversalProcessor._wait_loop(platform, send_reply, send_buttons, is_private, message_text)
        else:
            await send_reply(f"❌ **Injection Failed**\n\n{status}")
            if "editor zone" in status.lower() or "Targeting error" in status:
                await send_reply("🛠️ **Detected Targeting Error.** Launching automated self-fix...")
                # Note: Self-fix requires original bot context usually, we might skip for generic or implement generic self-fix
                pass

    @staticmethod
    def _sync_to_dashboard(user_id, text, attachments):
        try:
            chat_file = "/home/son/BANE/dashboard/chat_history.json"
            history = []
            if os.path.exists(chat_file):
                with open(chat_file, 'r') as f:
                    history = json.load(f)
            
            log_text = f"[User {user_id}] {text}"
            if attachments:
                log_text += f" [Attachments: {len(attachments)}]"
            
            history.append({
                "role": "user", 
                "text": log_text, 
                "user_id": user_id, 
                "time": datetime.now().isoformat()
            })
            
            if len(history) > 100: history = history[-100:]
            with open(chat_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.error(f"Dashboard sync failed: {e}")

    @staticmethod
    def _auto_sort_attachments(user_id, user_paths, attachments):
        """Attempts to move attachments to matching School subject folders."""
        school_dir = os.path.join(user_paths['workspace'], "School")
        if not os.path.exists(school_dir):
            return None
        
        subjects = [d for d in os.listdir(school_dir) if os.path.isdir(os.path.join(school_dir, d))]
        if not subjects:
            return None
            
        results = []
        import subprocess
        import shutil
        
        for att in attachments:
            path = att['path']
            filename = os.path.basename(path).lower()
            content = ""
            
            # Extract content for matching
            if path.lower().endswith('.pdf'):
                try:
                    proc = subprocess.run(['pdftotext', path, '-'], capture_output=True, text=True, timeout=5)
                    content = proc.stdout.lower()
                except: pass
            
            # Match strategy
            matched_subject = None
            for sub in subjects:
                # Clean subject name for matching (e.g. "COMP 026 - Principles of Systems Thinking" -> keywords)
                keywords = [k for k in sub.replace("-", " ").lower().split() if len(k) > 3]
                if any(kw in filename for kw in keywords) or (content and any(kw in content for kw in keywords)):
                    matched_subject = sub
                    break
            
            if matched_subject:
                dest_dir = os.path.join(school_dir, matched_subject)
                # If there's an 'Instructional Materials' or similar folder, prefer it
                for sub_dir in ["Instructional Materials", "Materials", "Notes"]:
                    if os.path.exists(os.path.join(dest_dir, sub_dir)):
                        dest_dir = os.path.join(dest_dir, sub_dir)
                        break
                
                try:
                    new_path = os.path.join(dest_dir, os.path.basename(path))
                    shutil.move(path, new_path)
                    att['path'] = new_path # Update path for injection context
                    results.append(f"• `{os.path.basename(path)}` → `{matched_subject}`")
                except Exception as e:
                    logger.error(f"Failed to move {filename}: {e}")
                    
        return "\n".join(results) if results else None

    @staticmethod
    async def _wait_loop(platform, send_reply, send_buttons, is_private, original_text):
        """
        Monitors Antigravity UI for completion/buttons.
        After AI finishes (idle), captures response via OCR and sends it back.
        """
        max_wait = 150
        waited = 0
        detected = False
        
        # Heuristic for detecting code edits
        is_code_edit = any(kw in original_text.lower() for kw in ["edit", "code", "change", "add", "remove", "update", "fix", "implement", "refactor"])

        while waited < max_wait:
            state = detect_state()
            
            # Check for buttons (File Changes)
            buttons = detect_action_buttons()
            if buttons:
                from agent.turbo import get_automation_state
                if get_automation_state()["autonomous"] and "accept_all" in buttons:
                    from antigravity.button_mapper import click_button
                    logger.info("⚡ Real-time Turbo: Auto-clicking Accept ALL")
                    click_button(buttons["accept_all"])
                    # Reset wait and continue monitoring for next step
                    waited = 0
                    await asyncio.sleep(5)
                    continue

                if send_buttons:
                    await send_buttons() # Trigger platform-specific button render
                detected = True
                break
            
            if state == "idle" and waited > 3.0:
                # Quick double check
                await asyncio.sleep(0.2)  # Reduced from 0.5s
                buttons = detect_action_buttons()
                if buttons and send_buttons:
                    await send_buttons()
                    detected = True
                break
            elif state == "error":
                return

            await asyncio.sleep(0.5)  # Increased from 0.15s to save CPU
            waited += 0.5
        
        if not detected and is_code_edit and is_private and send_buttons:
             # Fallback
             await send_buttons()

        # ============================================================
        # AI SELF-DELIVERY: The AI sends its own response via sender.py
        # (as instructed in AI_SKILLS). OCR capture was removed because
        # it caused duplicate/garbage responses — the OCR picked up raw
        # UI elements, context tags, and encrypted metadata from the screen.
        # ============================================================
        logger.info(f"✅ Wait loop complete for {platform}. AI will self-deliver response via sender.py.")


# --- Platform Handlers ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    TELEGRAM HANDLER (Legacy Adapter)
    Routes Telegram updates to UniversalProcessor.
    """
    user = update.effective_user
    if not user or not is_authorized(user.id):
        return

    from utils.user_manager import get_user_paths
    user_paths = get_user_paths(user.id)
    
    message = update.message
    message_text = message.text or message.caption or ""
    
    # Attachment Handling (Telegram Specific)
    attachments = []
    user_received_dir = user_paths["received"]
    
    try:
        file = None
        file_type = None
        if message.photo:
            file = await context.bot.get_file(message.photo[-1].file_id)
            file_type = "Image"
            dest = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        elif message.document:
            file = await context.bot.get_file(message.document.file_id)
            file_type = "Document"
            dest = message.document.file_name
        elif message.voice:
            file = await context.bot.get_file(message.voice.file_id)
            file_type = "Voice"
            dest = f"voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ogg"
        elif message.video:
            file = await context.bot.get_file(message.video.file_id)
            file_type = "Video"
            orig_name = message.video.file_name
            ext = os.path.splitext(orig_name)[1] if orig_name else ".mp4"
            dest = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        elif message.audio:
            file = await context.bot.get_file(message.audio.file_id)
            file_type = "Audio"
            orig_name = message.audio.file_name
            ext = os.path.splitext(orig_name)[1] if orig_name else ".mp3"
            dest = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        elif message.video_note:
            file = await context.bot.get_file(message.video_note.file_id)
            file_type = "VideoNote"
            dest = f"video_note_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        
        if file:
            full_dest = os.path.join(user_received_dir, dest)
            await file.download_to_drive(full_dest)
            attachments.append({"type": file_type, "path": os.path.abspath(full_dest)})
            
            # STT Hook
            if file_type == "Voice":
                try:
                    from utils.speech_to_text import transcribe_audio
                    transcript, error = transcribe_audio(os.path.abspath(full_dest))
                    if transcript:
                         message_text = f"[TRANSCRIPT]: \"{transcript}\"\n\n{message_text}"
                except Exception:
                    pass

    except Exception as e:
        logger.error(f"Attachment download failed: {e}")
        await update.message.reply_text(f"⚠️ Failed to receive attachment: {e}")

    # Persist ID, Content, and Attachments for Contextual Replies
    try:
        if message.message_id:
             mg_id = message.media_group_id if hasattr(message, "media_group_id") else None
             save_message(str(message.message_id), message_text, sender_id=str(user.id), attachments=attachments)
    except Exception as e:
        logger.error(f"Failed to save Telegram context: {e}")

    # --- MEDIA GROUP BUFFERING ---
    if hasattr(message, "media_group_id") and message.media_group_id:
        mg_id = message.media_group_id
        
        if not hasattr(handle_message, "_media_buffers"):
            handle_message._media_buffers = {}
            
        if mg_id not in handle_message._media_buffers:
            # Initialize buffer
            handle_message._media_buffers[mg_id] = {
                "attachments": [],
                "texts": [],
                "task": None,
                "update": update, # Store ref to first update
                "context": context,
                "reply_to": message.reply_to_message
            }
            
        buffer = handle_message._media_buffers[mg_id]
        buffer["attachments"].extend(attachments)
        if message_text:
            buffer["texts"].append(message_text)
            
        # Debounce: Cancel previous task if valid, set new one
        if buffer["task"]:
            buffer["task"].cancel()
            
        async def _deferred_mg_process():
            try:
                await asyncio.sleep(2.0) # Buffer window
                
                # Retrieve and clear buffer
                if mg_id in handle_message._media_buffers:
                    final_buf = handle_message._media_buffers.pop(mg_id)
                    
                    # Aggregate
                    final_atts = final_buf["attachments"]
                    # Clean empty usage
                    valid_texts = [t for t in final_buf["texts"] if t.strip()]
                    final_txt = "\n".join(valid_texts)
                    
                    logger.info(f"📚 Processing Media Group {mg_id}: {len(final_atts)} attachments, Text: '{final_txt[:30]}...'")
                    
                    from utils.user_manager import get_user_paths
                    u_paths = get_user_paths(final_buf["update"].effective_user.id)
                    
                    await _process_telegram_logic(
                        final_buf["update"], 
                        final_buf["context"], 
                        final_buf["update"].effective_user,
                        final_txt,
                        final_atts,
                        final_buf["reply_to"],
                        u_paths
                    )
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"Media Group Processing Error: {e}")

        buffer["task"] = asyncio.create_task(_deferred_mg_process())
        return # Stop individual processing

    # Shadow Protocol Commands
    if message_text.strip() == "/shadow_ON":
        set_shadow_state(True)
        await update.message.reply_text("🕶️ **SHADOW MODE: ONLINE**\n\n- Communications: Encrypted\n- Routing: Secure Tunnel\n- Isolation: ENABLED")
        return
    elif message_text.strip() == "/shadow_OFF":
        set_shadow_state(False)
        await update.message.reply_text("💼 **SHADOW MODE: OFFLINE**\n\n- Communications: Passive Logging\n- Routing: Standard Channel")
        return

    # Non-Group Message: Process Immediately
    await _process_telegram_logic(update, context, user, message_text, attachments, message.reply_to_message, user_paths)

async def _process_telegram_logic(update, context, user, message_text, attachments, reply_to_message, user_paths):
    """
    Extracted logic for processing a fully assembled Telegram message (single or grouped).
    """
    # Reply Context
    reply_context = ""
    if reply_to_message:
        try:
             # We rely on persistent history to get full details (incl attachments) of the parent
             from utils.message_history import get_message
             parent_msg = get_message(str(reply_to_message.message_id))
             
             if parent_msg:
                 sender = "System" if parent_msg.get("sender_id") == "system" else "User"
                 text = parent_msg.get("text", "[Unknown]")
                 reply_context = f"\n\n💬 **REPLY CONTEXT (Replying to {sender}):**\n> \"{text}\""
                 
                 hist_atts = parent_msg.get("attachments", [])
                 if hist_atts:
                      logger.info(f"📁 Adding {len(hist_atts)} historical attachments from Telegram reply.")
                      attachments.extend(hist_atts)
             else:
                 # Fallback if not in history
                 sender = "User" 
                 if reply_to_message.from_user.id == context.bot.id: sender = "System"
                 text = reply_to_message.text or reply_to_message.caption or "[Media]"
                 reply_context = f"\n\n💬 **REPLY CONTEXT (Replying to {sender}):**\n> \"{text}\""

        except Exception as e:
             logger.error(f"Reply Context Error: {e}")

    # Role
    chat = update.effective_chat
    role = "admin" if is_admin_context(update) else "guest"
    
    # Callbacks
    # Shadow Protocol Commands: Secure Reply Interceptor
    async def telegram_reply(text):
        # Decrypt if AI responded with ENC tag
        plain_text = decrypt_text(text)

        # Unified Sender Utility via Subprocess
        import subprocess
        cmd = [
            "/home/son/BANE/.venv/bin/python3",
            "/home/son/BANE/utils/sender.py",
            "--platform", "telegram",
            "--recipient_id", str(chat.id),
            "--text", plain_text
        ]

        # Voice handling via sender.py (if text to speech works seamlessly, or basic text)
        # For now, simplistic text reply via sender.py

        proc = await asyncio.to_thread(subprocess.run, cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            logger.error(f"Telegram Reply Failed (Subprocess): {proc.stderr}")


    async def telegram_buttons():
        # User explicitly requested to remove this ("Pa tangal nlng")
        pass

    await UniversalProcessor.process_request(
        platform="telegram",
        user_id=str(user.id),
        chat_id=str(chat.id),
        message_text=message_text,
        attachments=attachments,
        reply_context=reply_context,
        role=role,
        user_paths=user_paths,
        send_reply=telegram_reply,
        send_buttons=telegram_buttons,
        context_data={"is_private": chat.type == constants.ChatType.PRIVATE}
    )


async def handle_messenger_message(payload: dict, recipient_id: str, access_token: str):
    """
    MESSENGER HANDLER (New)
    Routes Messenger webhooks to UniversalProcessor.
    """
    # DEBUG: Log full payload to see what's actually looping
    logger.info(f"DEBUG_PAYLOAD: {json.dumps(payload)}")

    sender_id = payload.get('sender', {}).get('id')
    message_obj = payload.get('message', {})
    reaction_obj = payload.get('reaction')
    
    text = ""
    mid = ""
    
    if message_obj:
        text = message_obj.get('text', "")
        mid = message_obj.get('mid')
    elif reaction_obj:
        # Handle Reaction
        mid = reaction_obj.get('mid') # Original message ID
        emoji = reaction_obj.get('emoji', "")
        action = reaction_obj.get('action', "") # 'react' or 'unreact'
        
        if action == "react":
            parent_msg = get_message(mid)
            parent_text = parent_msg.get('text', '[Unknown content]') if parent_msg else '[Unknown content]'
            text = f"[REACTION]: User reacted with {emoji} to your message: \"{parent_text}\""
            logger.info(f"❤️ Reaction detected: {emoji} on {mid}")
        else:
            return # Ignore unreacts for now to save tokens

    # --- Start Automated Reaction Logic (Multilingual Atmospheric Analyzer) ---
    if mid and sender_id and not message_obj.get('is_echo'):
        msg_text_raw = message_obj.get('text', "") or ""
        has_attachments = 'attachments' in message_obj
        logger.info(f"🔍 Checking Auto-Reaction for: '{msg_text_raw[:30]}' (Attachments: {has_attachments})")
        
        try:
            from utils.emotion_lexicon import get_reaction_for_message, analyze_message_emotion
            
            # Get reaction from the multilingual atmospheric analyzer
            reaction_to_send = get_reaction_for_message(msg_text_raw, has_attachments=has_attachments)
            
            # Debug: log the emotion analysis result
            emotion, confidence, _ = analyze_message_emotion(msg_text_raw)
            if emotion:
                logger.info(f"🧠 Emotion Analysis: {emotion} (confidence: {confidence:.2f})")
            
        except ImportError as e:
            logger.error(f"⚠️ emotion_lexicon not available, falling back to basic: {e}")
            # Minimal fallback if module fails to load
            reaction_to_send = None
            msg_text_l = msg_text_raw.lower()
            if has_attachments:
                reaction_to_send = "❤️"
            elif any(kw in msg_text_l for kw in ["haha", "hehe", "lol", "😂", "🤣"]):
                reaction_to_send = "😂"
            elif any(kw in msg_text_l for kw in ["love", "thanks", "salamat", "galing", "❤️"]):
                reaction_to_send = "❤️"

        if reaction_to_send:
            async def trigger_auto_reaction(rid, m_id, react, tok):
                try:
                    logger.info(f"✨ Auto-Reacting with {react} to MID: {m_id}")
                    await asyncio.sleep(0.8) # Natural delay
                    # Subprocess React (Robust CLI Method)
                    import subprocess
                    cmd = [
                        "/home/son/BANE/.venv/bin/python3",
                        "/home/son/BANE/utils/sender.py",
                        "--platform", "messenger",
                        "--recipient_id", str(rid),
                        "--react", react,
                        "--msg_id", str(m_id)
                    ]
                    
                    proc = await asyncio.to_thread(subprocess.run, cmd, capture_output=True, text=True)
                    
                    if proc.returncode == 0:
                        logger.info(f"✅ Reaction {react} delivered (Subprocess).")
                    else:
                        logger.warning(f"⚠️ Reaction {react} failed: {proc.stderr}")
                except Exception as e:
                    logger.error(f"Auto-Reaction failed: {e}")
            
            asyncio.create_task(trigger_auto_reaction(sender_id, mid, reaction_to_send, access_token))
        else:
            logger.debug(f"No emotion match for: '{msg_text_raw[:30]}'")
    # --- End Automated Reaction Logic ---

    # Messenger often loops back the bot's own status messages as new inputs.
    SYSTEM_PREFIXES = ["⌛", "⚠️", "❌", "🔧", "✅"]
    if text and any(text.startswith(pref) for pref in SYSTEM_PREFIXES):
        logger.debug(f"Ignoring system message from {sender_id}: {text[:20]}...")
        return

    if message_obj.get('is_echo'):
        return
    
    #  Deduplication
    cache_key = mid
    if reaction_obj:
        cache_key = f"react_{mid}_{reaction_obj.get('action')}_{reaction_obj.get('emoji')}"

    if not hasattr(handle_messenger_message, "_mid_cache"):
        handle_messenger_message._mid_cache = set()
    
    if cache_key in handle_messenger_message._mid_cache:
        logger.debug(f"Ignoring duplicate Messenger event: {cache_key}")
        return
    
    handle_messenger_message._mid_cache.add(cache_key)
    if len(handle_messenger_message._mid_cache) > 100:
        handle_messenger_message._mid_cache.remove(next(iter(handle_messenger_message._mid_cache)))

    if not sender_id: return

    # User Auth & Paths
    from utils.user_manager import get_user_paths, initialize_user
    is_new, notice = initialize_user(sender_id, platform="messenger")
    
    if is_new and notice:
        subprocess.Popen([
            "/home/son/BANE/.venv/bin/python3", "/home/son/BANE/utils/sender.py", 
            "--platform", "messenger", "--recipient_id", str(sender_id), "--text", notice
        ])
    
    user_paths = get_user_paths(sender_id, platform="messenger")
    role = "admin" if str(sender_id) == os.getenv("MESSENGER_ADMIN_ID", "ADMIN_MESSENGER_ID") else "guest"

    # Admin Commands (Messenger)
    if text and text.strip().lower() == "/reset_quota":
        from core import cortex_recall
        cortex_recall.clear_quota_state()
        subprocess.Popen([
            "/home/son/BANE/.venv/bin/python3", "/home/son/BANE/utils/sender.py",
            "--platform", "messenger", "--recipient_id", str(sender_id), 
            "--text", "✅ **Quota State Cleared.** Live AI model is now re-enabled."
        ])
        return

    # Shadow Mode Toggle (Messenger)
    msg_upper = text.strip().upper() if text else ""
    if "/SHADOW_ON" in msg_upper or "SHADOW ON" in msg_upper:
        set_shadow_state(True)
        subprocess.Popen([
            "/home/son/BANE/.venv/bin/python3", "/home/son/BANE/utils/sender.py",
            "--platform", "messenger", "--recipient_id", str(sender_id), 
            "--text", "🕶️ SHADOW MODE: ONLINE\nComms: Encrypted"
        ])
        return
    elif "/SHADOW_OFF" in msg_upper or "SHADOW OFF" in msg_upper:
        set_shadow_state(False)
        subprocess.Popen([
            "/home/son/BANE/.venv/bin/python3", "/home/son/BANE/utils/sender.py",
            "--platform", "messenger", "--recipient_id", str(sender_id), 
            "--text", "💼 SHADOW MODE: OFFLINE\nComms: Log Only"
        ])
        return

    # --- AUTO ENGAGE MODE HANDLERS ---
    clean_text = text.strip().upper() if text else ""
    if "BANE ACTIVATE AUTO ENGAGE MODE" in clean_text:
        from antigravity.skill_manager import set_current_skill
        set_current_skill("AUTO_ENGAGE")
        
        # Launch background loop
        engage_script = os.path.join(user_paths['workspace'], "auto_engage.py")
        if os.path.exists(engage_script):
            subprocess.Popen([sys.executable, engage_script], start_new_session=True)
            subprocess.Popen([
                "/home/son/BANE/.venv/bin/python3", "/home/son/BANE/utils/sender.py",
                "--platform", "messenger", "--recipient_id", str(sender_id), 
                "--text", "🚀 **BANE AUTO-ENGAGE MODE: ACTIVATED**\n\nAnalytical Thinking Core: ONLINE\nLoop Status: ENGAGED\n\nI am now exploring and engaging autonomously."
            ])
        else:
            subprocess.Popen([
                "/home/son/BANE/.venv/bin/python3", "/home/son/BANE/utils/sender.py",
                "--platform", "messenger", "--recipient_id", str(sender_id), 
                "--text", "❌ **Auto-Engage Script not found.** Creation failed."
            ])
        return

    if "BANE DEACTIVE AUTO ENGAGE MODE" in clean_text or "BANE DEACTIVATE AUTO ENGAGE MODE" in clean_text:
        from antigravity.skill_manager import set_current_skill
        set_current_skill("WORKSPACE") # Back to default
        
        # Stop background loop
        stop_flag = os.path.join(user_paths['workspace'], "auto_engage.stop")
        with open(stop_flag, "w") as f:
            f.write("STOP")
            
        subprocess.Popen([
            "/home/son/BANE/.venv/bin/python3", "/home/son/BANE/utils/sender.py",
            "--platform", "messenger", "--recipient_id", str(sender_id), 
            "--text", "🛑 **BANE AUTO-ENGAGE MODE: DEACTIVATED**\n\nReturning to standard command mode."
        ])
        return

    # Attachments
    attachments = []
    if 'attachments' in message_obj:
        import requests
        user_received_dir = user_paths["received"]
        
        for att in message_obj['attachments']:
            try:
                att_type = att['type']
                url = att['payload'].get('url')
                if not url: continue
                
                import posixpath
                from urllib.parse import urlparse
                path = urlparse(url).path
                ext = posixpath.splitext(path)[1]
                if not ext:
                    if att_type == 'image': ext = '.jpg'
                    elif att_type == 'audio': ext = '.mp3'
                    elif att_type == 'video': ext = '.mp4'
                    else: ext = '.file'
                
                filename = f"{att_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
                dest_path = os.path.join(user_received_dir, filename)
                
                res = await asyncio.to_thread(requests.get, url, stream=True, timeout=30)
                res.raise_for_status()
                with open(dest_path, 'wb') as f:
                    for chunk in res.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                attachments.append({
                    "type": att_type.capitalize(),
                    "path": os.path.abspath(dest_path)
                })
                logger.info(f"Downloaded Messenger attachment: {filename}")
            except Exception as e:
                logger.error(f"Failed to download Messenger attachment: {e}")

    # Persist MID
    try:
        if mid:
            save_message(mid, text, sender_id=sender_id, attachments=attachments)
            
        mid_file = "/home/son/BANE/storage/last_user_mids.json"
        data = {}
        if os.path.exists(mid_file):
            with open(mid_file, 'r') as f:
                data = json.load(f)
        data[str(sender_id)] = mid
        with open(mid_file, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        logger.error(f"Failed to save Messenger context: {e}")

    # Callbacks (Messenger)
    async def messenger_reply(text):
        # Decrypt if AI responded with ENC tag
        plain_text = decrypt_text(text)
        try:
            # Replicated CLI Approach: Use subprocess to ensure fresh environment/state
            import subprocess
            cmd = [
                "/home/son/BANE/.venv/bin/python3",
                "/home/son/BANE/utils/sender.py",
                "--platform", "messenger",
                "--recipient_id", str(sender_id),
                "--text", plain_text
            ]
            if mid:
                cmd.extend(["--reply_to", str(mid)])

            # Run strictly like the successful manual attempt
            process = await asyncio.to_thread(
                subprocess.run, 
                cmd, 
                capture_output=True, 
                text=True,
                check=False
            )
            
            if process.returncode == 0:
                logger.info(f"✅ Messenger Reply Sent (Subprocess). Output: {process.stdout.strip()}")
                # Attempt to parse MID from output for history
                import re
                mid_match = re.search(r"ID: (mid\.[$A-Za-z0-9\-_]+)", process.stdout)
                if mid_match:
                     try: save_message(mid_match.group(1), plain_text, sender_id="system")
                     except: pass
            else:
                logger.error(f"❌ Messenger Reply Failed (Subprocess): {process.stderr}")

        except Exception as e:
            logger.error(f"Messenger Async Reply Failed: {e}")

    async def messenger_buttons():
        pass

    # Reply Context Extraction
    reply_context = ""
    reply_to = message_obj.get("reply_to")
    logger.info(f"📎 Reply-To Debug: reply_to={reply_to}")
    if reply_to:
        reply_mid = reply_to.get("mid")
        if reply_mid:
            parent_msg = get_message(reply_mid)
            logger.info(f"📎 Reply-To Lookup: mid={reply_mid[:20]}... found={parent_msg is not None}")
            if parent_msg:
                 txt = parent_msg.get("text") or ""
                 hist_atts = parent_msg.get("attachments", [])
                 if not txt.strip() and hist_atts:
                     txt = f"[Attached {hist_atts[0]['type']}]"
                 if len(txt) > 150:
                     txt = txt[:147] + "..."
                 sender_label = "System" if parent_msg.get("sender_id") == "system" else "User"
                 reply_context = f"\n💬 Reply to {sender_label}: \"{txt}\""
                 # Include attachment paths so the AI can identify/access referenced files
                 if hist_atts:
                      att_lines = []
                      for att in hist_atts:
                          att_lines.append(f"📎 {att.get('type', 'File')}: `{att.get('path', 'unknown')}`")
                      reply_context += "\n" + "\n".join(att_lines)
                      attachments.extend(hist_atts)
            else:
                 # Fallback: parent message not in our history (e.g. sent via shadow_send.py)
                 logger.warning(f"⚠️ Reply-To MID {reply_mid[:20]}... NOT found in message_history!")
                 reply_context = f"\n💬 Reply to a previous message (context unavailable)"

    # ============================================================
    # ⚡ CORTEX RECALL / LIGHT MODE BYPASS
    # ============================================================
    # Priority zero-token response path.
    if text and not reaction_obj:
        from core import cortex_recall
        u_hash = user_paths.get('hash', '?')
        q_fallback = cortex_recall.handle_quota_mode(u_hash, text, bool(attachments))
        
        # LOGIC REFINEMENT:
        # 1. If quota IS exceeded, we MUST bypass (always use q_fallback if valid).
        # 2. If quota is FINE, we ONLY bypass for very high confidence (Static or SmartRecall > 0.8).
        
        is_limit = cortex_recall.is_quota_exceeded()
        # Refined recall: 80% similarity threshold to ensure 'sentence-level' matching
        # Note: school_fallback only bypasses if quota is exceeded to prevent annoying triggers on general questions.
        # Smart Recall (cortex_recall) still bypasses if confidence > 0.8.
        is_strong_match = False
        if q_fallback:
            mode = q_fallback["mode"]
            conf = q_fallback.get("confidence", 0)
            
            if mode == "static":
                is_strong_match = True
            elif mode == "cortex_recall" and conf > 0.8:
                is_strong_match = True
            elif mode == "school_fallback" and is_limit:
                is_strong_match = True
        
        if is_limit or is_strong_match:
            if q_fallback and q_fallback["mode"] != "quota_block":
                logger.info(f"⚡ CORTEX BYPASS [{q_fallback['mode']}]: '{text[:20]}...' (Limit={is_limit}, Confidence={q_fallback.get('confidence')})")
                await messenger_reply(q_fallback["text"])
                return
    # ============================================================
    # ============================================================

    await UniversalProcessor.process_request(
        platform="messenger",
        user_id=str(sender_id),
        chat_id=str(sender_id),
        message_text=text,
        attachments=attachments,
        reply_context=reply_context, 
        role=role,
        user_paths=user_paths,
        send_reply=messenger_reply,
        send_buttons=messenger_buttons,
        context_data={"is_private": True, "reply_to_mid": mid} 
    )
