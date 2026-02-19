# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
import zipfile
import os
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from telegram_interface.auth import is_authorized

logger = logging.getLogger(__name__)

# Files/Dirs to exclude from snapshot for security/size
EXCLUDE = [
    "secrets.env", 
    ".env", # Explicitly exclude env files
    "__pycache__", 
    ".git", 
    ".venv", 
    "venv", 
    "node_modules",
    "vendor",
    "storage",
    ".gemini", 
    ".pytest_cache",
    ".mypy_cache",
    "Debug",
]

PROJECTS_ROOT = "/home/son/BANE_Workspaces"
BANE_ROOT = "/home/son/BANE"

def should_exclude(path: str) -> bool:
    """Checks if a path should be excluded."""
    # Exclude specific extensions
    if path.endswith((".pyc", ".zip", ".mp3", ".png", ".jpg", ".jpeg", ".exe", ".so", ".dll")):
        return True

    parts = path.split(os.sep)
    for part in parts:
        if part in EXCLUDE or part.startswith("."):
            if part != "." and part != "..":
                return True
    return False

async def save_snapshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Creates and sends a ZIP snapshot of a project or the core system."""
    user = update.effective_user
    if not user or not is_authorized(user.id):
        return

    args = context.args
    
    # 1. No arguments: List available projects
    if not args:
        if not os.path.exists(PROJECTS_ROOT):
            await update.message.reply_text("❌ Workspaces directory not found.")
            return

        projects = [d for d in os.listdir(PROJECTS_ROOT) if os.path.isdir(os.path.join(PROJECTS_ROOT, d))]
        projects.sort()

        if not projects:
            await update.message.reply_text("📂 **Available Workspaces:**\n\n(No projects found in Workspaces/)\n\nTo save the system core, use: `/save core`.")
            return

        project_list = "\n".join([f"📁 `{p}`" for p in projects])
        await update.message.reply_text(
            f"📂 **Available Workspaces:**\n\n{project_list}\n\n"
            f"💡 **Usage:** `/save <project_name>`\n"
            f"💡 **Core:** `/save core`"
        )
        return

    target = args[0].strip()
    
    # 2. Handle "core" target
    if target.lower() == "core":
        source_dir = BANE_ROOT
        zip_name = f"bane_core_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        display_name = "BANE Core"
        # For core, we exclude workspace folders if they were somehow left inside
        current_exclude = EXCLUDE + ["BANE_Workspaces"]
    else:
        # 3. Handle Project target
        source_dir = os.path.join(PROJECTS_ROOT, target)
        if not os.path.exists(source_dir):
            await update.message.reply_text(f"❌ Project `{target}` not found in Workspaces/ directory.")
            return
        
        # 📋 PREVIEW: Show user what files are available
        files_preview = []
        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d not in EXCLUDE and not d.startswith(".")]
            for f in files:
                if not should_exclude(os.path.join(root, f)):
                    rel_path = os.path.relpath(os.path.join(root, f), source_dir)
                    files_preview.append(f"📄 `{rel_path}`")
                if len(files_preview) >= 10: break
            if len(files_preview) >= 10: break
            
        preview_text = "\n".join(files_preview)
        if len(files_preview) >= 10: preview_text += "\n...and more."
        
        await update.message.reply_text(f"🔍 **Available files in {target}:**\n\n{preview_text}")
        
        zip_name = f"{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        display_name = f"Project: {target}"
        current_exclude = EXCLUDE

    await update.message.reply_text(f"📦 Zipping **{display_name}**...\n(Libraries and resource files will be excluded for speed)")

    try:
        count = 0
        zip_path = os.path.join("/tmp", zip_name)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Change directory to source_dir for clean zip structure
            original_cwd = os.getcwd()
            os.chdir(source_dir)
            
            for root, dirs, files in os.walk("."):
                # Prune excluded directories in-place
                dirs[:] = [d for d in dirs if d not in current_exclude and not d.startswith(".")]
                
                for file in files:
                    full_path = os.path.normpath(os.path.join(root, file))
                    # Check against global exclude logic
                    if not should_exclude(full_path) and file != zip_name:
                        zipf.write(full_path)
                        count += 1
            
            os.chdir(original_cwd)

        if count == 0:
            await update.message.reply_text("⚠️ No files found to zip (or all files were excluded).")
            if os.path.exists(zip_path): os.remove(zip_path)
            return

        await update.message.reply_text(f"📤 Uploading {display_name} ({count} files)...")
        
        with open(zip_path, "rb") as f:
            await update.message.reply_document(
                document=f, 
                caption=f"🗄️ {display_name} Snapshot",
                write_timeout=300
            )
        
        if os.path.exists(zip_path):
            os.remove(zip_path)
        logger.info(f"Sent {display_name} zip to {user.first_name}")

    except Exception as e:
        logger.error(f"Save failed: {e}")
        await update.message.reply_text(f"❌ Save failed: {e}")
        if 'original_cwd' in locals(): os.chdir(original_cwd)
        if os.path.exists(zip_path): os.remove(zip_path)
