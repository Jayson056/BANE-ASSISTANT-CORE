# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import logging
import os
import asyncio
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TimedOut, NetworkError
from telegram_interface.auth import is_authorized

from agent.screen import screen_command
from agent.report import report_command
from core.router import handle_message

# Load environment variables
from dotenv import load_dotenv
load_dotenv(dotenv_path="config/secrets.env")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ... imports ...
from telegram.ext import CallbackQueryHandler
from security.confirm import resolve_confirmation
from agent.router import route_command, COMMANDS, COMMAND_DESCRIPTIONS
from security.password_flow import is_awaiting_password, set_password, inject_password, set_awaiting_password
from security.detector import detect_password_prompt
from security.sudo_flow import is_awaiting_sudo, get_pending_sudo_action, set_sudo_password, execute_with_sudo
from core.router import handle_message as core_handle_message
from agent.sysrest import execute_system_restart, is_awaiting_restart_confirmation, handle_restart_confirmation
from agent.syslogout import execute_system_logout
from agent.select_skill import is_awaiting_skill_password, verify_skill_password, handle_skill_selection
from telegram import BotCommand

# Wrapper to intercept messages for password flow only (confirmation handled by buttons now)
async def handle_message_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user: return
    
    # 0. Check Restart Confirmation (Highest Priority after Auth)
    if is_awaiting_restart_confirmation(user.id):
        if await handle_restart_confirmation(update, context):
            return

    auth_ok, notice = is_authorized(user.id)
    if not auth_ok:
        return
    
    if notice:
        await update.message.reply_text(notice)

    message = update.message
    text = message.text or message.caption
    
    # 🛡️ SECURITY: Auto-delete sensitive messages (Passwords, Paths, tokens)
    if text:
        from utils.sender import contains_sensitive_info
        if contains_sensitive_info(text) or text.strip().startswith("/pass"):
            try:
                await message.delete()
                logger.info(f"🛡️ Sensitive message from {user.id} auto-deleted in real-time.")
                # Optional: send a temporary notice or just proceed
            except Exception as e:
                logger.warning(f"Failed to auto-delete sensitive message: {e}")

    # ⚡ AUTO-REACTION (Mirrors Messenger behavior — fire and forget)
    has_attachment = any([message.photo, message.document, message.voice, message.audio, message.video])
    if text or has_attachment:
        try:
            msg_text_raw = text or ""
            chat_id = update.effective_chat.id
            msg_id = message.message_id
            
            async def _auto_react():
                try:
                    from utils.emotion_lexicon import get_reaction_for_message, analyze_message_emotion
                    reaction_to_send = get_reaction_for_message(msg_text_raw, has_attachments=has_attachment)
                    
                    if reaction_to_send:
                        # Small natural delay before reacting
                        import asyncio as _aio
                        await _aio.sleep(0.5)
                        from utils.sender import set_message_reaction
                        result = await asyncio.to_thread(
                            set_message_reaction, chat_id, msg_id, reaction_to_send
                        )
                        if result:
                            emotion, confidence, _ = analyze_message_emotion(msg_text_raw)
                            logger.info(f"✨ Telegram Auto-React: {reaction_to_send} [{emotion}, {confidence:.2f}] on msg {msg_id}")
                        else:
                            logger.debug(f"Telegram reaction delivery failed for msg {msg_id}")
                except Exception as e:
                    logger.debug(f"Auto-reaction skipped: {e}")
            
            asyncio.create_task(_auto_react())
        except Exception:
            pass  # Never let reaction logic block message handling

    
    if not text and not has_attachment:
        return

    # Log user message to conversation history (Isolated)
    try:
        from utils.logger import log_conversation_step
        chat = update.effective_chat
        is_group = chat.type in [constants.ChatType.GROUP, constants.ChatType.SUPERGROUP]
        
        log_content = text or ""
        if is_group:
            log_content = f"👥 [Group: {chat.title}] {log_content}"
            
        if has_attachment:
            attachments = []
            if message.photo: attachments.append(f"[Photo: {message.photo[-1].file_id}]")
            if message.document: attachments.append(f"[Document: {message.document.file_name}]")
            if message.voice: attachments.append("[Voice Message]")
            if message.audio: attachments.append(f"[Audio: {message.audio.file_name or 'unnamed'}]")
            if message.video: attachments.append(f"[Video: {message.video.file_name or 'unnamed'}]")
            log_content += "\n" + "\n".join(attachments)
        
        log_conversation_step(log_content.strip(), "user", user_id=user.id)
    except Exception as e:
        logger.error(f"Failed to log user message: {e}")

    # 1. Check Sudo Password Flow
    if is_awaiting_sudo():
        try:
            await update.message.delete()
        except:
            pass
            
        action = get_pending_sudo_action()
        set_sudo_password(text)
        
        if action == "SYSTEM_RESTART":
            success, error = execute_with_sudo(["reboot"])
            if success:
                await update.message.reply_text("🔄 Rebooting system now...")
            else:
                await update.message.reply_text(f"❌ Reboot failed: {error}")
        elif action == "SYSTEM_LOGOUT":
            success, error = execute_with_sudo(["gnome-session-quit", "--logout", "--no-prompt"])
            if success:
                await update.message.reply_text("👋 Logging out...")
            else:
                await update.message.reply_text(f"❌ Logout failed: {error}")
        return

    # 2. Check Screen Lock Password Flow
    if is_awaiting_password():
        try:
            await update.message.delete()
        except:
            pass
            
        set_password(text)
        success = inject_password()
        if success:
            await update.message.reply_text("🔑 Password injected and wiped from memory.")
        else:
            await update.message.reply_text("❌ Failed to inject password.")
        return

    # 3. Check Skill Password Flow
    if is_awaiting_skill_password(user.id):
        await verify_skill_password(update, context)
        return

    # 3.5 Check Skill Text Command (Reply Keyboard)
    from agent.select_skill import handle_skill_text_command
    if await handle_skill_text_command(update, context):
        return

    # 4. Standard Antigravity Injection
    try:
        await core_handle_message(update, context)
    except (TimedOut, NetworkError) as e:
        logger.error(f"Network issue during message handling: {e}")
        try:
            await update.message.reply_text("📶 **NETWORK ISSUE DETECTED**\n\nThe connection to Telegram timed out. Please **send your message again** to ensure it reaches the bane core.")
        except Exception:
            pass # Silent failure if even the error message fails
    except Exception as e:
        logger.error(f"Unexpected error in message handler: {e}")
        try:
            await update.message.reply_text(f"⚠️ **UNEXPECTED ERROR**\n\nSomething went wrong: `{str(e)}`")
        except Exception:
            pass

async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Automatically initialize data environments for new group members and log join events."""
    from utils.user_manager import initialize_user
    from utils.logger import log_conversation_step
    import json
    
    if not update.message or not update.message.new_chat_members:
        return
        
    chat = update.effective_chat
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            logger.info(f"🦅 BANE joined group: {chat.title} ({chat.id})")
            log_conversation_step(f"🦅 BANE (Bot) joined the group: {chat.title} (Chat ID: {chat.id})", "system")
            continue
            
        if not member.is_bot:
            # 1. Initialize user directories
            is_new, notice = initialize_user(member.id)
            
            # 2. Check for custom welcome configuration
            custom_welcome = None
            welcome_file = "config/custom_welcomes.json"
            if os.path.exists(welcome_file):
                try:
                    with open(welcome_file, "r") as f:
                        welcomes = json.load(f)
                        # Match by ID, Full Name, First Name, or Username
                        lookups = [str(member.id), member.full_name, member.first_name, member.username]
                        for key in lookups:
                            if key and key in welcomes:
                                custom_welcome = welcomes[key]
                                break
                except Exception as e:
                    logger.error(f"Failed to load custom welcomes: {e}")

            # 3. Deliver welcome message
            if custom_welcome:
                await update.message.reply_text(custom_welcome)
            elif is_new:
                logger.info(f"🆕 Automatically created isolated DATA-USER environment for: {member.full_name} ({member.id})")
                await update.message.reply_text(f"✅ **Welcome {member.first_name}!**\n\nI have automatically initialized a private, isolated workspace for you. You can now interact with me casually in this group or via private message.")
            else:
                logger.debug(f"User {member.id} already initialized.")
            
            # 4. Log the arrival (Isolated)
            log_conversation_step(f"👋 Joined the group: {chat.title} (ID: {chat.id})", "system", user_id=member.id)
            log_conversation_step(f"👤 User {member.full_name} ({member.id}) joined the group: {chat.title}", "system")

async def handle_bot_membership_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle when the bot itself is added or removed from a chat."""
    from utils.logger import log_conversation_step
    result = update.my_chat_member
    chat = result.chat
    
    if result.new_chat_member.status == "member":
        logger.info(f"Added to chat: {chat.title} ({chat.id})")
        log_conversation_step(f"📡 BANE ADMITTED to chat: {chat.title} (Chat ID: {chat.id})", "system")
    elif result.new_chat_member.status in ["kicked", "left"]:
        logger.info(f"Removed from chat: {chat.title} ({chat.id})")
        log_conversation_step(f"📉 BANE REMOVED from chat: {chat.title} (Chat ID: {chat.id})", "system")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Inline Button clicks."""
    query = update.callback_query
    logger.info(f"Button clicked by {query.from_user.id} ({query.data})")
    
    # ALWAYS answer the callback first to stop loading spinner
    try:
        await query.answer()
    except Exception as e:
        logger.error(f"Failed to answer callback query: {e}")

    data = query.data
    user_id = query.from_user.id
    logger.info(f"Processing callback data: {data} from user {user_id}")
    
    try:
        # Handle Model Selection buttons
        if data.startswith("MODEL:"):
            await handle_model_selection(query)
            return
        elif data.startswith("SKILL:"):
            await handle_skill_selection(query, context)
            return
        elif data == "CLICK_MODEL_DROPDOWN":
            from antigravity.model_selector import click_model_dropdown
            await query.edit_message_text("🖱️ Clicking model selector in UI...")
            success, model = click_model_dropdown()
            if success:
                await query.message.reply_text(f"✅ Clicked model selector. Current model: {model}")
            else:
                await query.message.reply_text("❌ Failed to click model selector.")
            return
        
        # Handle Turbo buttons
        if data.startswith("TURBO:"):
            from agent.turbo import handle_turbo_callback
            await handle_turbo_callback(query)
            return
        
        # Handle Accept/Reject ALL buttons
        if data == "ACCEPT_ALL":
            await handle_accept_all(query)
            return
        elif data == "REJECT_ALL":
            await handle_reject_all(query)
            return
        
        # Handle Allow Access buttons
        if data == "ALLOW_ONCE":
            await handle_allow_access(query, "allow_once")
            return
        elif data == "ALLOW_CONV":
            await handle_allow_access(query, "allow_conv")
            return
        
        # Handle confirmation buttons (YES:ACTION / NO:ACTION)
        if ":" not in data:
            return

        decision, action = data.split(":", 1)
        
        # Resolve against pending
        result = resolve_confirmation(user_id, decision)
        
        # STATELESS FALLBACK: Allow critical system actions even if memory was wiped
        if result is None and decision == "YES" and action in ["SYSTEM_RESTART", "SYSTEM_LOGOUT"]:
            from telegram_interface.auth import is_authorized
            auth_ok, _ = is_authorized(user_id)
            if auth_ok:
                result = action
                logger.info(f"Stateless confirmation accepted for {action} by user {user_id}")
        
        if result:
            await query.edit_message_text(f"✅ Action confirmed: {result}")
            
            # Dispatch execution
            if result == "SYSTEM_RESTART":
                await execute_system_restart(update, context)
            elif result == "SYSTEM_LOGOUT":
                await execute_system_logout(update, context)
            else:
                await query.message.reply_text(f"⚠️ Action '{result}' confirmed but no handler found.")
                
        else:
            if decision == "NO":
                await query.edit_message_text(f"❌ Action cancelled: {action}")
            else:
                await query.edit_message_text("⚠️ Confirmation expired or invalid.")
    
    except Exception as e:
        logger.error(f"Error in button_handler for data '{data}': {e}")
        try:
            await query.message.reply_text(f"⚠️ Button action failed: {str(e)[:200]}")
        except:
            pass

async def handle_allow_access(query, access_type: str):
    """Handle Allow Once / Allow Conversation buttons for directory access."""
    from antigravity.button_mapper import detect_action_buttons, click_button
    
    await query.edit_message_text(f"🔍 Processing {access_type.replace('_', ' ').title()}...")
    
    buttons = detect_action_buttons()
    if buttons and access_type in buttons:
        success = click_button(buttons[access_type])
        if success:
            await query.edit_message_text(f"✅ Access granted ({access_type.replace('_', ' ')})")
        else:
            await query.message.reply_text(f"❌ Failed to click {access_type} button in UI.")
    else:
        await query.edit_message_text("⚠️ Access button not found in UI. It may have been processed already.")

async def handle_model_selection(query):
    """Handle model selection button click."""
    from antigravity.model_selector import select_model_by_name
    
    # Extract model name from callback data
    model_name = query.data.replace("MODEL:", "")
    
    await query.edit_message_text(f"🔄 Switching to {model_name}...")
    
    # Click the model in Antigravity UI and check for limits
    success, is_limited, message = select_model_by_name(model_name)
    
    if success:
        if is_limited:
            await query.message.reply_text(f"⚠️ **{model_name} selected**\n\n{message}\n\nYou may need to switch to a different model if it stops responding.")
        else:
            await query.message.reply_text(f"✅ **{model_name} selected**\n\nThe ai model has been successfully updated.")
    else:
        await query.message.reply_text(f"❌ **switch failed**\n\n{message}\n\nMake sure the bane engine is visible.")


async def handle_accept_all(query):
    """Click Accept ALL button in Antigravity UI, then clean up the notification."""
    from antigravity.button_mapper import detect_action_buttons, click_button
    import asyncio
    
    # Immediately edit to remove keyboard and show processing status
    await query.edit_message_text("🔍 Processing Accept...")
    
    # Offload OCR detection to thread
    buttons = await asyncio.to_thread(detect_action_buttons)
    if buttons and "accept_all" in buttons:
        success = await asyncio.to_thread(click_button, buttons["accept_all"])
        if success:
            # Brief confirmation then delete the notification message entirely
            await query.edit_message_text("✅ Changes accepted")
            await asyncio.sleep(2)
            try:
                await query.message.delete()
            except Exception:
                pass  # Already gone or can't delete — no problem
        else:
            await query.edit_message_text("❌ Failed to click accept button in UI.")
    else:
        await query.edit_message_text("⚠️ Accept button not found in UI. It may have been processed already.")
        await asyncio.sleep(3)
        try:
            await query.message.delete()
        except Exception:
            pass

async def handle_reject_all(query):
    """Click Reject ALL button in Antigravity UI, then clean up the notification."""
    from antigravity.button_mapper import detect_action_buttons, click_button
    import asyncio
    
    # Immediately edit to remove keyboard and show processing status
    await query.edit_message_text("🔍 Processing Reject...")
    
    # Offload OCR detection to thread
    buttons = await asyncio.to_thread(detect_action_buttons)
    if buttons and "reject_all" in buttons:
        success = await asyncio.to_thread(click_button, buttons["reject_all"])
        if success:
            # Brief confirmation then delete the notification message entirely
            await query.edit_message_text("❌ Changes rejected")
            await asyncio.sleep(2)
            try:
                await query.message.delete()
            except Exception:
                pass
        else:
            await query.edit_message_text("❌ Failed to click reject button in UI.")
    else:
        await query.edit_message_text("⚠️ Reject button not found in UI. It may have been processed already.")
        await asyncio.sleep(3)
        try:
            await query.message.delete()
        except Exception:
            pass

async def security_monitor(context: ContextTypes.DEFAULT_TYPE):
    """Background job to detect password prompts, access requests, and quota limits."""
    user_id = os.getenv("TELEGRAM_USER_ID")
    if not user_id:
        return

    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    loop = asyncio.get_running_loop()

    # 1. Check for Password Prompts
    if not is_awaiting_password():
        # Offload blocking OCR to thread
        is_prompt = await loop.run_in_executor(None, detect_password_prompt)
        if is_prompt:
            set_awaiting_password(True)
            await context.bot.send_message(
                chat_id=user_id, 
                text="🔑 **KEYRING AUTHENTICATION REQUIRED**\n\nA system keyring or authentication prompt has been detected.\n\nSend your password and I'll auto-paste it into the input box for you."
            )

    # 2. Check for Directory Access Prompts (Allow Once / Allow Conversation)
    from antigravity.button_mapper import detect_action_buttons
    # Offload blocking OCR to thread
    buttons = await loop.run_in_executor(None, detect_action_buttons)
    
    if buttons and ("allow_once" in buttons or "allow_conv" in buttons):
        from telegram_interface.ui import allow_access_keyboard
        # Check if we already alerted (simple rate limit using job_data)
        last_alert = context.job.data.get("last_access_alert", 0) if context.job.data else 0
        import time
        if time.time() - last_alert > 60: # Alert once per minute
            if context.job.data is None: context.job.data = {}
            context.job.data["last_access_alert"] = time.time()
            
            await context.bot.send_message(
                chat_id=user_id,
                text="🛡️ **DIRECTORY ACCESS REQUESTED**\n\nBANE is asking for permission to access your files.\n\nChoose an option below:",
                reply_markup=allow_access_keyboard()
            )

    # 2.5 Autonomous Acceptance (TURBO MODE)
    # Disabled per user request ("Pa tangal nlng") - OCR was detecting text in editor as buttons
    # from agent.turbo import get_automation_state
    # if get_automation_state()["autonomous"]:
    #     buttons = await loop.run_in_executor(None, detect_action_buttons)
    #     if buttons and "accept_all" in buttons:
    #         from antigravity.button_mapper import click_button
    #         logger.info("🚀 Autonomous Mode: Auto-clicking 'Accept ALL'")
    #         success = click_button(buttons["accept_all"])
    #         if success:
    #             # Silenced notification per user request ("Pa tangal nlng")
    #             # await context.bot.send_message(chat_id=user_id, text="⚡ **TURBO**: Automatically accepted core changes.")
    #             pass

    # 3. Check for AI Quota Limits (PROACTIVE)
    from antigravity.quota_detector import detect_quota_popup
    # Offload blocking OCR to thread
    quota_data = await loop.run_in_executor(None, detect_quota_popup)
    btn_coords, limit_model = quota_data if quota_data else (None, None)
    if btn_coords:
        last_limit_alert = context.job.data.get("last_limit_alert", 0) if context.job.data else 0
        import time
        if time.time() - last_limit_alert > 300: # Alert once per 5 mins
            if context.job.data is None: context.job.data = {}
            context.job.data["last_limit_alert"] = time.time()
            
            # Sanitize model name to prevent Markdown parsing errors
            import html
            from antigravity.quota_detector import sanitize_text
            safe_model = html.escape(sanitize_text(str(limit_model)))
            
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"⚠️ <b>AI QUOTA REACHED</b>\n\nThe current model (<b>{safe_model}</b>) has hit its usage limit.\n\nUse /select_model to switch to another model now.",
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.warning(f"Failed to send HTML quota alert: {e}")
                # Fallback to plain text
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"⚠️ AI QUOTA REACHED\n\nThe current model ({safe_model}) has hit its usage limit.\n\nUse /select_model to switch to another model now."
                )

async def post_init(application):
    """Setup commands menu in Telegram."""
    commands_list = []
    for cmd, desc in COMMAND_DESCRIPTIONS.items():
        commands_list.append(BotCommand(cmd, desc))
    
    await application.bot.set_my_commands(commands_list)
    logger.info("Bot command menu initialized.")

async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and notify the admin."""
    logger.error(f"Uncaught Exception: {context.error}")
    
    # Notify Admin if possible
    user_id = os.getenv("TELEGRAM_USER_ID")
    if user_id:
        try:
            error_details = str(context.error)
            # Truncate for Telegram safety
            if len(error_details) > 300: error_details = error_details[:300] + "..."
            
            await context.bot.send_message(
                chat_id=user_id,
                text=f"🔴 **CRITICAL SYSTEM ERROR**\n\nBANE hit an unexpected exception:\n`{error_details}`\n\nCheck logs for full traceback."
            )
        except:
            pass

def run_bot():
    if not TOKEN or TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ No valid TELEGRAM_BOT_TOKEN found in config/secrets.env")
        return

    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .post_init(post_init)
        .connect_timeout(30)
        .read_timeout(30)
        .build()
    )
    
    # Register error handler
    application.add_error_handler(global_error_handler)
    
    # Register commands
    for cmd_triggers in COMMANDS.keys():
        command_name = cmd_triggers.lstrip("/")
        application.add_handler(CommandHandler(command_name, route_command))

    # Register Message Handler (Wrapped) - Accept ALL non-command messages (text + attachments)
    application.add_handler(MessageHandler((~filters.COMMAND), handle_message_wrapper))
    
    # Register New Chat Member Handler for automatic initialization
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_member))
    
    # Register Bot Membership Change Handler
    from telegram.ext import ChatMemberHandler
    application.add_handler(ChatMemberHandler(handle_bot_membership_change, ChatMemberHandler.MY_CHAT_MEMBER))

    # Register Callback Handler (Buttons)
    application.add_handler(CallbackQueryHandler(button_handler))

    # Register Background Jobs
    if application.job_queue:
        # Reduced frequency to 30s to free up CPU for faster AI responses
        application.job_queue.run_repeating(security_monitor, interval=30, first=5)

    print("🦅 BANE Bot is polling...")
    application.run_polling()

if __name__ == "__main__":
    run_bot()
