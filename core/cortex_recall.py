# BANE - Cortex Recall System
# Copyright (c) 2026 Jayson056. All rights reserved.
#
# 3-Layer Architecture:
#   Layer 1: Live AI (uses model quota)
#   Layer 2: Cortex Memory (stored structured responses)
#   Layer 3: Response Engine (sends without calling model)
#
# This module handles Layer 2 + Layer 3.

import json
import os
import time
import re
import logging
from datetime import datetime
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

# ============================================================
# PATHS
# ============================================================
CORTEX_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "cortex")
CORTEX_GLOBAL = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "cortex_memory.json")
QUOTA_STATE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "states", "quota_state.json")

# ============================================================
# STATIC RESPONSE BANK (Zero-Token, Rule-Based)
# ============================================================
# These responses are returned instantly without any AI call.
# Supports multilingual patterns (English + Tagalog + common greetings).

STATIC_RESPONSES = {
    # --- Greetings ---
    "greetings": {
        "patterns": [
            r"^(hi|hello|hey|yo|sup|musta|kamusta|kumusta|magandang|good\s*(morning|afternoon|evening|night)|uy|hoy|oi|bro|boss|bes|bestie|pre|mare|pare)\b",
            r"^(ohayo|konnichiwa|annyeong|hola|bonjour|ciao|merhaba|namaste)\b",
        ],
        "responses": [
            "Uy Boss! 👋 Kamusta? Anong maitutulong ko?",
            "Yo! 🤙 Ready ako. Ano ang kailangan mo?",
            "Boss! Andiyan na ko. 🫡 Ano ang mission?",
        ],
    },
    # --- Status Check ---
    "status": {
        "patterns": [
            r"^(status|estado|lagay|anong\s*lagay|how\s*are\s*you|kamusta\s*ka|ok\s*ka|buhay\s*ka|alive|running|gumagana)\b",
            r"^(system\s*status|health\s*check|ping)\b",
        ],
        "responses": [
            "All systems OPERATIONAL! ⚡🟢 CPU stable, memory clean, connections live. Ready for tasks, Boss!",
        ],
    },
    # --- Acknowledgments ---
    "acknowledgment": {
        "patterns": [
            r"^(ok|okay|okey|oks|sige|ge|got\s*it|noted|copy|roger|understood|alright|aight|bet|nice|cool|tama|solid|ayos)\s*[.!]*$",
        ],
        "responses": [
            "Got it, Boss! 👍",
            "Copy! ✅",
            "Noted! 🫡",
        ],
    },
    # --- Thanks ---
    "thanks": {
        "patterns": [
            r"^(thanks|thank\s*you|thank\s*u|ty|tysm|salamat|maraming\s*salamat|tnx|thx|thanx|arigatou|gracias|merci|danke|grazie)\b",
        ],
        "responses": [
            "Walang anuman, Boss! 😊 Tawag mo lang ako anytime!",
            "Always ready to serve! 🫡❤️",
        ],
    },
    # --- Goodbye ---
    "goodbye": {
        "patterns": [
            r"^(bye|goodbye|see\s*ya|later|paalam|aalis\s*na|matulog\s*na|goodnight|gn|sleep|tulog)\b",
        ],
        "responses": [
            "Take care, Boss! 🫡 Nandito lang ako pag kailangan mo. Goodnight! 🌙",
            "Sige Boss, pahinga ka muna! I'll keep watch. 🛡️⚡",
        ],
    },
    # --- Affirmative Reactions (not questions, just expressions) ---
    "expression": {
        "patterns": [
            r"^(haha|hehe|hihi|lol|lmao|rofl|😂|🤣|😆|💀)\s*$",
            r"^(wow|grabe|nice|lupet|galing|astig|sheesh|fire|🔥|❤️|👍)\s*[!]*$",
        ],
        "responses": None,  # No text reply needed — handled by reaction system
    },
}

# ============================================================
# QUOTA STATE MANAGEMENT
# ============================================================

def get_quota_state() -> dict:
    """
    Reads the current quota state from the state file.
    Returns: {
        "is_exceeded": bool,
        "model": str,
        "detected_at": str (ISO timestamp),
        "error_message": str,
        "degradation_level": int (0=normal, 1=reduced, 2=cached_only)
    }
    """
    try:
        if os.path.exists(QUOTA_STATE_FILE):
            with open(QUOTA_STATE_FILE, 'r') as f:
                state = json.load(f)
            
            # Auto-expire after 4 hours (quota resets usually happen periodically)
            detected_at = state.get("detected_at", "")
            if detected_at:
                detected_time = datetime.fromisoformat(detected_at)
                elapsed = (datetime.now() - detected_time).total_seconds()
                if elapsed > 14400:  # 4 hours
                    logger.info("Quota state expired (>4h), resetting to normal")
                    clear_quota_state()
                    return {"is_exceeded": False, "degradation_level": 0}
            
            return state
    except Exception as e:
        logger.error(f"Error reading quota state: {e}")
    
    return {"is_exceeded": False, "degradation_level": 0}


def set_quota_state(error_message: str = "", model: str = ""):
    """Mark quota as exceeded."""
    os.makedirs(os.path.dirname(QUOTA_STATE_FILE), exist_ok=True)
    state = {
        "is_exceeded": True,
        "model": model,
        "detected_at": datetime.now().isoformat(),
        "error_message": error_message,
        "degradation_level": 2,  # Full cached mode
        "consecutive_errors": get_quota_state().get("consecutive_errors", 0) + 1,
    }
    try:
        with open(QUOTA_STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        logger.warning(f"⚠️ Quota state set: EXCEEDED (model: {model})")
    except Exception as e:
        logger.error(f"Error saving quota state: {e}")


def clear_quota_state():
    """Reset quota state to normal."""
    try:
        if os.path.exists(QUOTA_STATE_FILE):
            os.remove(QUOTA_STATE_FILE)
            logger.info("✅ Quota state cleared — back to normal mode")
    except Exception as e:
        logger.error(f"Error clearing quota state: {e}")


def is_quota_exceeded() -> bool:
    """Quick check if quota is currently exceeded."""
    return get_quota_state().get("is_exceeded", False)


# ============================================================
# CORTEX MEMORY OPERATIONS
# ============================================================

def _load_cortex_global() -> list:
    """Load the global cortex memory bank."""
    try:
        if os.path.exists(CORTEX_GLOBAL):
            with open(CORTEX_GLOBAL, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading cortex memory: {e}")
    return []


def _save_cortex_global(memories: list):
    """Save the global cortex memory bank."""
    try:
        with open(CORTEX_GLOBAL, 'w') as f:
            json.dump(memories, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving cortex memory: {e}")


def _load_user_cortex(user_hash: str) -> dict:
    """Load per-user cortex memory."""
    os.makedirs(CORTEX_DIR, exist_ok=True)
    path = os.path.join(CORTEX_DIR, f"{user_hash}.json")
    try:
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading user cortex for {user_hash}: {e}")
    return {"last_prompt": None, "last_response": None, "history": []}


def _save_user_cortex(user_hash: str, data: dict):
    """Save per-user cortex memory."""
    os.makedirs(CORTEX_DIR, exist_ok=True)
    path = os.path.join(CORTEX_DIR, f"{user_hash}.json")
    try:
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving user cortex for {user_hash}: {e}")


def _text_similarity(a: str, b: str) -> float:
    """
    Calculate similarity between two strings.
    Uses SequenceMatcher for fuzzy matching.
    """
    if not a or not b:
        return 0.0
    a_clean = re.sub(r'[^\w\s]', '', a.lower().strip())
    b_clean = re.sub(r'[^\w\s]', '', b.lower().strip())
    return SequenceMatcher(None, a_clean, b_clean).ratio()


# ============================================================
# STORE: Save AI responses to Cortex Memory
# ============================================================

def store_cortex(user_hash: str, user_message: str, ai_response: str):
    """
    Store a successful AI response in cortex memory.
    Called AFTER every successful AI generation.
    
    Stores both:
    1. Per-user memory (for fast last-response recall)
    2. Global memory bank (for cross-user smart recall)
    """
    if not user_message or not ai_response:
        return
    
    # Skip storing very short or system messages
    if len(ai_response.strip()) < 10:
        return
    
    timestamp = datetime.now().isoformat()
    
    # 1. Per-User Memory (last response + history)
    try:
        user_data = _load_user_cortex(user_hash)
        user_data["last_prompt"] = user_message
        user_data["last_response"] = ai_response
        user_data["last_timestamp"] = timestamp
        
        # Keep history (max 200 entries to ensure long-term recall)
        history = user_data.get("history", [])
        history.append({
            "query": user_message[:500],  # Truncate long messages
            "response": ai_response[:2000],  # Truncate long responses
            "timestamp": timestamp,
        })
        if len(history) > 200:
            history = history[-200:]
        user_data["history"] = history
        
        _save_user_cortex(user_hash, user_data)
        logger.debug(f"🧠 Cortex stored for user {user_hash}: '{user_message[:40]}...'")
    except Exception as e:
        logger.error(f"Failed to store per-user cortex: {e}")
    
    # 2. Global Memory Bank (check for duplicate first)
    try:
        memories = _load_cortex_global()
        
        # Check if a similar query already exists (>0.85 similarity)
        for mem in memories:
            if _text_similarity(mem.get("query", ""), user_message) > 0.85:
                # Update existing entry with newer response
                mem["response"] = ai_response[:2000]
                mem["timestamp"] = timestamp
                mem["hits"] = mem.get("hits", 0)
                _save_cortex_global(memories)
                logger.debug(f"🧠 Cortex updated existing entry for: '{user_message[:40]}...'")
                return
        
        # Add new entry
        memories.append({
            "query": user_message[:500],
            "response": ai_response[:2000],
            "timestamp": timestamp,
            "hits": 0,
        })
        
        # Cap at 1000 entries (remove oldest with least hits)
        if len(memories) > 1000:
            memories.sort(key=lambda x: (x.get("hits", 0), x.get("timestamp", "")))
            memories = memories[-1000:]
        
        _save_cortex_global(memories)
        logger.info(f"🧠 Cortex stored NEW entry: '{user_message[:40]}...'")
    except Exception as e:
        logger.error(f"Failed to store global cortex: {e}")


# ============================================================
# RECALL: Retrieve stored responses
# ============================================================

def recall_last_response(user_hash: str) -> dict | None:
    """
    Recall the last valid AI response for a user.
    Returns: {"query": str, "response": str, "timestamp": str} or None
    """
    try:
        user_data = _load_user_cortex(user_hash)
        if user_data.get("last_response"):
            return {
                "query": user_data.get("last_prompt", ""),
                "response": user_data["last_response"],
                "timestamp": user_data.get("last_timestamp", ""),
            }
    except Exception as e:
        logger.error(f"Recall error for {user_hash}: {e}")
    return None


def smart_recall(user_hash: str, new_input: str, threshold: float = 0.65) -> dict | None:
    """
    Smart recall: Find the most similar stored response to the new input.
    
    Search order:
    1. Per-user history (higher priority for personalized responses)
    2. Global memory bank (cross-user knowledge)
    
    Returns: {"query": str, "response": str, "similarity": float, "source": str} or None
    """
    if not new_input or len(new_input.strip()) < 5:
        return None
    
    best_match = None
    best_score = 0.0
    
    # 1. Search per-user history first
    try:
        user_data = _load_user_cortex(user_hash)
        for entry in user_data.get("history", []):
            sim = _text_similarity(new_input, entry.get("query", ""))
            if sim > best_score and sim >= threshold:
                best_score = sim
                best_match = {
                    "query": entry["query"],
                    "response": entry["response"],
                    "similarity": sim,
                    "source": "user_cortex",
                    "timestamp": entry.get("timestamp", ""),
                }
    except Exception as e:
        logger.error(f"User cortex search error: {e}")
    
    # 2. Search global memory bank
    try:
        memories = _load_cortex_global()
        for mem in memories:
            sim = _text_similarity(new_input, mem.get("query", ""))
            if sim > best_score and sim >= threshold:
                best_score = sim
                best_match = {
                    "query": mem["query"],
                    "response": mem["response"],
                    "similarity": sim,
                    "source": "global_cortex",
                    "timestamp": mem.get("timestamp", ""),
                }
                # Increment hit counter
                mem["hits"] = mem.get("hits", 0) + 1
        
        if best_match and best_match["source"] == "global_cortex":
            _save_cortex_global(memories)
    except Exception as e:
        logger.error(f"Global cortex search error: {e}")
    
    if best_match:
        logger.info(f"🧠 Cortex RECALL: similarity={best_score:.2f}, source={best_match['source']}, query='{new_input[:40]}...'")
    
    return best_match


# ============================================================
# STATIC MATCH: Check against pre-built response bank
# ============================================================

def check_static_response(message: str) -> str | None:
    """
    Check if a message matches any static response pattern.
    Returns the response text, or None if no match.
    """
    if not message or len(message.strip()) < 1:
        return None
    
    msg_clean = message.strip().lower()
    
    for category, data in STATIC_RESPONSES.items():
        for pattern in data["patterns"]:
            try:
                if re.search(pattern, msg_clean, re.IGNORECASE):
                    responses = data.get("responses")
                    if responses is None:
                        # Category exists but no text reply needed (e.g., expressions)
                        return None
                    # Return a response (rotate based on time for variety)
                    import hashlib
                    idx = int(hashlib.md5(msg_clean.encode()).hexdigest(), 16) % len(responses)
                    logger.info(f"📋 Static response matched: category='{category}', message='{msg_clean[:30]}'")
                    return responses[idx]
            except re.error:
                pass
    
    return None


# ============================================================
# MAIN QUOTA HANDLER: The unified entry point
# ============================================================

def handle_quota_mode(user_hash: str, user_message: str, has_attachments: bool = False) -> dict:
    """
    Main handler when quota is exceeded or as a pre-check.
    
    Returns: {
        "mode": "static" | "cortex_recall" | "cortex_last" | "school_fallback" | "quota_block",
        "text": str (the response to send),
        "confidence": float (0-1, how confident we are in this response)
    }
    """
    # 1. Try Static Responses first (instant, zero cost)
    static = check_static_response(user_message)
    if static:
        return {
            "mode": "static",
            "text": static,
            "confidence": 1.0,
        }
    
    # 2. Try Smart Recall (similarity matching)
    recalled = smart_recall(user_hash, user_message, threshold=0.8)
    if recalled:
        prefix = "🧠 **CORTEX RECALL** (Stored Response)\n\n"
        return {
            "mode": "cortex_recall",
            "text": f"{prefix}{recalled['response']}",
            "confidence": recalled["similarity"],
        }
    
    # 3. Try School Fallback for school-related queries
    SCHOOL_KEYWORDS = [
        "assignment", "task", "deadline", "todo", "sched", "schedule",
        "class", "subject", "sub", "friday", "monday", "tuesday",
        "wednesday", "thursday", "saturday", "exam", "holiday", "school",
        "gawa", "project", "milestone", "event",
    ]
    # Regex-based whole-word matching to avoid false positives (e.g., 'gawa' matching 'nagagawa')
    pattern = r"\b(" + "|".join(re.escape(kw) for kw in SCHOOL_KEYWORDS) + r")\b"
    if re.search(pattern, user_message.lower()):
        try:
            from utils.school_helper import get_school_fallback_response
            fallback = get_school_fallback_response(user_hash, user_message)
            if fallback and "not found" not in fallback.lower():
                return {
                    "mode": "school_fallback",
                    "text": f"🎓 **SCHOOL DATA** (Local Tracker)\n\n{fallback}",
                    "confidence": 0.9,
                }
        except Exception as e:
            logger.error(f"School fallback error: {e}")
    
    # 4. Try last response as absolute fallback (ONLY if quota is actually exceeded)
    if is_quota_exceeded():
        last = recall_last_response(user_hash)
        if last:
            return {
                "mode": "cortex_last",
                "text": (
                    "⚠️ **QUOTA REACHED** — AI model temporarily unavailable.\n\n"
                    "🧠 Heto ang last stored response ko:\n\n"
                    f"{last['response']}\n\n"
                    "💡 Subukan mo ulit mamaya kapag nag-reset na ang quota."
                ),
                "confidence": 0.3,
            }
    
    # 5. Final fallback — nothing stored or quota reached but no cache
    if is_quota_exceeded():
        return {
            "mode": "quota_block",
            "text": (
                "⚠️ **QUOTA REACHED**\n\n"
                "Naka-limit na ang AI model at wala pa akong stored response para sa tanong mo.\n\n"
                "Pwede mong subukan:\n"
                "• Itanong ulit mamaya (quota resets periodically)\n"
                "• Mag-ask ng school-related questions (may local data ako)\n"
                "• Mag-send ng simple commands (may static responses ako)"
            ),
            "confidence": 0.0,
        }
    
    return None # No fallback needed, let it proceed to AI


# ============================================================
# DEGRADATION LEVEL HELPER
# ============================================================

def get_degradation_config() -> dict:
    """
    Returns processing configuration based on current degradation level.
    
    Level 0 (Normal):    Full AI, full context, TTS enabled
    Level 1 (Reduced):   Full AI, reduced context, no TTS
    Level 2 (Cached):    No AI call, cortex-only, no TTS
    """
    state = get_quota_state()
    level = state.get("degradation_level", 0)
    
    if level >= 2:
        return {
            "level": 2,
            "label": "CACHED_ONLY",
            "use_ai": False,
            "use_tts": False,
            "max_context_tokens": 0,
            "inject_skill_header": False,
            "inject_footer": False,
        }
    elif level == 1:
        return {
            "level": 1,
            "label": "REDUCED",
            "use_ai": True,
            "use_tts": False,
            "max_context_tokens": 500,
            "inject_skill_header": False,
            "inject_footer": False,
        }
    else:
        return {
            "level": 0,
            "label": "NORMAL",
            "use_ai": True,
            "use_tts": True,
            "max_context_tokens": None,  # No limit
            "inject_skill_header": True,
            "inject_footer": True,
        }
