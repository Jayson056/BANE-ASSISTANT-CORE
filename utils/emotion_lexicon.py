# BANE - Multilingual Emotion Lexicon & Atmospheric Sentiment Analyzer
# Supports: English, Tagalog/Filipino, Spanish, French, Japanese, Korean,
#           Portuguese, Indonesian/Malay, German, Italian, Arabic, Hindi,
#           Thai, Vietnamese, Chinese (Pinyin), Cebuano, Ilocano
# Created: 2026-02-16
# Copyright (c) 2026 Jayson056. All rights reserved.

import re
import unicodedata

# ============================================================
# EMOTION CATEGORIES & THEIR REACTION EMOJI
# ============================================================
# Each category maps to a reaction emoji that Meta Messenger supports.
# Messenger supports: 😍❤️😂😮😢😠👍👎🥰🔥
# We use a subset for auto-reactions.

REACTION_MAP = {
    "joy":        "😂",   # Laughter, amusement, fun
    "love":       "❤️",   # Love, appreciation, gratitude, affection
    "surprise":   "😮",   # Shock, disbelief, amazement
    "agreement":  "👍",   # Confirmation, acknowledgement, approval
    "sadness":    "😢",   # Sadness, sympathy, disappointment
    "fire":       "🔥",   # Hype, impressive, exciting
    "attachment": "❤️",   # Default for sent files/images (appreciation)
}

# ============================================================
# MULTILINGUAL EMOTION LEXICON
# ============================================================
# Structure: emotion_category -> list of keywords/patterns
# Keywords are all lowercase. The analyzer normalizes input before matching.
# Includes common misspellings, slang, internet shorthand, and emoticons.

LEXICON = {
    "joy": {
        "keywords": [
            # English
            "haha", "hahaha", "hahahaha", "hehe", "hehehe", "hihi", "hoho",
            "lol", "lmao", "lmfao", "rofl", "roflmao", "xd", "xdd",
            "funny", "hilarious", "comedy", "joke", "kidding", "joking",
            "laughing", "cracking up", "dying", "dead", "im dead",
            # Internet/Meme
            "💀", "😂", "🤣", "😆", "😹", "🫡",
            "kekw", "pepega", "kek", "topkek", "copium",
            "bruh moment", "no cap", "fr fr", "ong", "on god",
            "sus", "based", "sheeesh", "sheesh",
            # Tagalog/Filipino
            "hahahah", "wahaha", "bwahaha", "jajaja",
            "nakakatawa", "tawa", "kaloka", "charot", "char",
            "lodi", "petmalu", "werpa", "dasurv", "naur",
            "awit", "HAHAHAHH", "antindi", "antindiii",
            "grabe ka", "alam mo na", "eme", "chos", "chz",
            "jologs", "jejemon", "wala na finish na",
            "tawang tawa", "natatawa", "pamatay",
            "kabado pero tawa", "luh", "jusko tawa",
            # Spanish
            "jaja", "jajaj", "jajaja", "jajajaja", "jejeje",
            "gracioso", "divertido", "chistoso", "risa",
            "muerto de risa", "me muero", "qué risa",
            # French
            "mdr", "ptdr", "lol", "xptdr", "mort de rire",
            "trop drôle", "drole", "hilarant", "marrant",
            # Japanese
            "wwww", "www", "笑", "ワロタ", "草", "くさ",
            "ウケる", "面白い", "おもしろい", "爆笑",
            "ぷぷぷ", "あはは", "えへへ",
            # Korean
            "ㅋㅋㅋ", "ㅋㅋ", "ㅎㅎㅎ", "ㅎㅎ",
            "웃기다", "웃겨", "재밌어", "재밌다",
            "빵터짐", "ㅋㅋㅋㅋ", "ㄱㅋ",
            # Portuguese
            "kkk", "kkkk", "kkkkk", "rsrs", "rsrsrs",
            "huahua", "engraçado", "engraçada", "rindo",
            # Indonesian/Malay
            "wkwk", "wkwkwk", "wkwkwkwk", "awkwk",
            "lucu", "ngakak", "wakaka", "hahay",
            "asik", "mantap", "gokil",
            # German
            "hahaha", "witzig", "lustig", "lächerlich",
            # Italian
            "ahahah", "divertente", "ridere", "morto dal ridere",
            # Arabic (transliterated)
            "ههههه", "هههه", "ههه", "خخخ",
            "يضحك", "مضحك",
            # Hindi (transliterated)
            "hahaha", "mazaak", "mazak", "mazaa",
            "hasna", "hasi", "masti",
            # Thai
            "5555", "55555", "555+",
            "ขำ", "ตลก", "หัวเราะ",
            # Vietnamese
            "hahaha", "hihi", "hehe",
            "vui", "buồn cười", "hài",
            # Chinese (Pinyin / chars)
            "哈哈", "哈哈哈", "哈哈哈哈",
            "笑死", "笑死我了", "太搞笑了",
            # Cebuano
            "hahay", "katawa", "nalingaw",
            # Ilocano
            "kastoy", "nakatkatawa",
        ],
        # Regex patterns for flexible matching (e.g., "haha" repeated any number of times)
        "patterns": [
            r"h[ae]{2,}h[ae]*",          # haha, hahaha, hehe, hahahahaha etc
            r"w{0,1}k{2,}",              # wkwk, kkk etc (but not single k)
            r"j[ae]{2,}j[ae]*",          # jaja, jajaja etc
            r"ㅋ{2,}",                   # Korean laugh
            r"ㅎ{2,}",                   # Korean chuckle
            r"w{3,}",                    # Japanese www
            r"5{3,}",                    # Thai laughing (555...)
            r"x{1}d{1,}",               # xd, xdd
            r"r[s]{2,}r?s?",            # rsrs, rsrsrs (Portuguese)
            r"ه{3,}",                   # Arabic hahaha
            r"哈{2,}",                   # Chinese haha
        ],
    },

    "love": {
        "keywords": [
            # English
            "love", "love it", "love this", "i love", "loved",
            "thanks", "thank you", "thank u", "thx", "thanx", "tysm", "tyvm",
            "appreciate", "appreciated", "grateful", "gratitude",
            "amazing", "awesome", "wonderful", "beautiful", "gorgeous",
            "perfect", "excellent", "brilliant", "fantastic", "fabulous",
            "incredible", "magnificent", "stunning", "superb", "outstanding",
            "great job", "well done", "good job", "nice work", "keep it up",
            "best", "the best", "goat", "legend", "legendary",
            "blessed", "wholesome", "heartwarming",
            "respect", "respects", "salute",
            "cute", "adorable", "sweet", "sweetheart",
            # Emoticons
            "❤️", "💕", "💖", "💗", "💙", "💚", "🧡", "💛", "💜", "🖤", "🤍",
            "😍", "🥰", "😘", "😻", "💞", "💓", "💝", "🫶", "🥺",
            "♥", "♡", "❣️",
            # Tagalog/Filipino
            "mahal", "mahal kita", "labyu", "lab u", "laby",
            "salamat", "salamat po", "maraming salamat",
            "galing", "ang galing", "ang galing mo",
            "lupet", "ang lupet", "grabe galing",
            "idol", "idolo", "boss", "bes", "bestie",
            "sana all", "kilig", "kinikilig", "natutuwa",
            "gandang ganda", "maganda", "pogi", "gwapo",
            "astig", "aliw", "nakakatuwa",
            "saludo", "pogi mo", "ganda mo",
            "napakagaling", "salute boss",
            "mwah", "mwa", "mwaps", "muah", "muahh",
            # Spanish
            "gracias", "muchas gracias", "amor", "te amo", "te quiero",
            "hermoso", "hermosa", "increíble", "genial", "maravilloso",
            "excelente", "perfecto", "fantástico", "fenomenal",
            "guapo", "guapa", "bonito", "bonita",
            # French
            "merci", "merci beaucoup", "amour", "je t'aime",
            "magnifique", "formidable", "superbe", "génial",
            "beau", "belle", "adorable", "parfait",
            # Japanese
            "ありがとう", "ありがとうございます", "感謝", "大好き",
            "愛してる", "素晴らしい", "素敵", "最高",
            "すごい", "かわいい", "きれい", "美しい",
            "好き", "大好き", "嬉しい", "やった",
            "神", "サイコー", "イケメン",
            # Korean
            "감사", "감사합니다", "고마워", "사랑해",
            "좋아", "좋아해", "최고", "멋져", "멋있어",
            "짱", "예쁘다", "귀여워", "잘했어",
            "아이돌", "존", "존잘", "존예",
            # Portuguese
            "obrigado", "obrigada", "amor", "te amo",
            "incrível", "maravilhoso", "maravilhosa",
            "lindo", "linda", "perfeito", "perfeita",
            # Indonesian/Malay
            "terima kasih", "makasih", "cinta", "sayang",
            "keren", "hebat", "bagus", "mantap", "jempol",
            # German
            "danke", "vielen dank", "liebe", "wunderbar",
            "toll", "großartig", "perfekt", "schön",
            # Italian
            "grazie", "mille grazie", "amore", "ti amo",
            "bellissimo", "bellissima", "perfetto", "fantastico",
            "bravo", "bravissimo",
            # Arabic (transliterated)
            "شكرا", "حب", "احبك", "جميل", "رائع",
            "شكراً", "ممتاز", "عظيم",
            # Hindi (transliterated)
            "dhanyavaad", "shukriya", "pyaar", "pyar",
            "bahut accha", "zabardast", "kamaal",
            "mast", "badiya", "shaandaar",
            # Thai
            "ขอบคุณ", "รัก", "สวย", "เก่ง", "ดีมาก",
            "เยี่ยม", "สุดยอด",
            # Vietnamese
            "cảm ơn", "yêu", "tuyệt vời", "tuyệt",
            "đẹp", "giỏi", "hay quá",
            # Chinese
            "谢谢", "爱你", "太棒了", "厉害", "漂亮",
            "好看", "完美", "牛逼", "牛",
            # Cebuano
            "salamat", "maayo", "gwapa", "gwapo", "nindot",
            # Ilocano
            "agyamanak", "napintas", "naimbag",
        ],
        "patterns": [
            r"❤️?",
            r"mw+a+h*",                # mwah, muah, mwa, etc
            r"l[ao]b\s*y[ou]?",       # labyu, laby, lab u
        ],
    },

    "surprise": {
        "keywords": [
            # English
            "wow", "woah", "whoa", "omg", "oh my god", "oh my",
            "wtf", "wth", "what the", "no way", "seriously",
            "unbelievable", "insane", "crazy", "mind blown",
            "shocking", "shocked", "stunned", "speechless",
            "impossible", "unreal", "holy", "holy cow", "holy shit",
            "damn", "dang", "dayum", "yoo", "yooo",
            # Emoticons
            "😱", "😮", "😲", "🤯", "😧", "😦", "🫢", "😳",
            "🤭", "‼️", "⁉️", "❗", "❕",
            # Tagalog/Filipino
            "hala", "grabe", "jusko", "jusmio", "ay",
            "diyos ko", "naku", "nakupo", "sus", "susmaryosep",
            "luh", "luhh", "talaga", "totoo ba", "seryoso",
            "ano", "anoh", "di ko kinaya", "bongga",
            "grabeh", "nakakaloka", "nakakagulat",
            "hay nako", "aba", "shet", "shuta", "puta",
            "putangina", "tangina", "gago", "weh", "wehh",
            # Spanish
            "¡dios mío!", "dios mio", "increíble", "no puede ser",
            "madre mía", "qué locura", "impresionante", "guau",
            "ostras", "hostia", "joder", "vaya",
            # French
            "oh la la", "mon dieu", "incroyable", "c'est pas vrai",
            "putain", "merde", "waouh", "impressionnant",
            # Japanese
            "えっ", "マジ", "マジで", "すごっ", "やばい",
            "うそ", "嘘", "信じられない", "ありえない",
            "なにこれ", "びっくり", "え!?",
            # Korean
            "대박", "헐", "진짜", "진짜?", "말도 안돼",
            "미쳤다", "미쳐", "세상에", "어머",
            "실화", "레전드", "ㄷㄷ", "ㄷㄷㄷ",
            # Portuguese
            "caramba", "meu deus", "nossa", "uau",
            "impossível", "sério", "não acredito",
            # Indonesian/Malay
            "ya ampun", "astaga", "gila", "serius",
            "tidak mungkin", "waduh", "anjir", "anjay",
            # German
            "mein gott", "wahnsinn", "unglaublich", "krass",
            # Italian
            "mamma mia", "porca miseria", "incredibile", "assurdo",
            # Arabic
            "يا الله", "مستحيل", "مش معقول",
            # Hindi
            "are", "arey", "yaar", "kya baat",
            "pagal", "sach me", "sachchi",
            # Thai
            "โอ้", "ไม่จริง", "เว้ย", "โคตร",
            # Vietnamese
            "trời ơi", "ối", "không thể tin được",
            # Chinese
            "天啊", "不会吧", "真的假的", "卧槽", "我去",
            # Cebuano
            "ay", "grabe", "unsa", "tinuod ba",
        ],
        "patterns": [
            r"w+o+[ah]*",             # wow, woah, woahhh
            r"o+m+g+",               # omg, ommgg
            r"y+o+o+",               # yoo, yooo
            r"w+t+f+",               # wtf
            r"ㄷ{2,}",               # Korean surprise
        ],
    },

    "agreement": {
        "keywords": [
            # English
            "yes", "yeah", "yep", "yup", "yea", "ye",
            "ok", "okay", "okey", "k", "kk",
            "sure", "absolutely", "definitely", "certainly",
            "right", "correct", "exactly", "precisely",
            "agree", "agreed", "true", "facts", "fax",
            "bet", "bet!", "say less", "word",
            "done", "got it", "roger", "copy", "understood",
            "nice", "cool", "alright", "aight", "ight",
            "legit", "valid", "fair", "fair enough",
            # Emoticons
            "👍", "👌", "✅", "☑️", "✔️", "🫡", "💯",
            # Tagalog/Filipino
            "oo", "oho", "opo", "sige", "ge",
            "mismo", "solid", "ayos", "tama", "tamah",
            "g", "gg", "go", "gora", "lets go", "tara",
            "copy", "noted", "gets", "gets na",
            "oks", "okie", "oki", "okidoki",
            "yan", "ayan", "eto", "ito",
            "paki", "pakifix", "pakicheck", "pakiupdate",
            "replace", "update", "fix", "check", "run",
            "gawa", "gawin", "edit", "change",
            # Spanish
            "sí", "si", "vale", "claro", "por supuesto",
            "de acuerdo", "bien", "bueno", "correcto",
            "dale", "listo", "hecho",
            # French
            "oui", "ouais", "d'accord", "bien sûr",
            "exactement", "tout à fait", "ça marche", "ok",
            # Japanese
            "はい", "うん", "そう", "そうだね",
            "了解", "分かった", "わかった", "オッケー",
            "そうそう", "だよね", "ね",
            # Korean
            "네", "응", "그래", "맞아", "좋아",
            "알겠어", "알겠습니다", "ㅇㅇ", "ㅇㅋ",
            # Portuguese
            "sim", "claro", "certo", "tá", "tá bom",
            "beleza", "fechou", "combinado",
            # Indonesian/Malay
            "iya", "ya", "oke", "siap", "baik", "beres",
            "setuju", "betul",
            # German
            "ja", "jawohl", "genau", "richtig", "stimmt",
            "in ordnung", "klar",
            # Italian
            "sì", "certo", "esatto", "va bene", "perfetto",
            # Arabic
            "نعم", "أيوه", "تمام", "ماشي",
            # Hindi
            "haan", "ha", "theek", "sahi", "bilkul",
            "accha", "chalega",
            # Thai
            "ครับ", "ค่ะ", "ได้", "ใช่", "โอเค",
            # Vietnamese
            "vâng", "ừ", "được", "ok", "đúng",
            # Chinese
            "好的", "对", "是的", "行", "没问题", "OK",
            # Cebuano
            "oo", "sige", "sakto",
        ],
        "patterns": [
            r"o+k+",                  # ok, okk, okkk
            r"k+k+",                  # kk, kkk (not the laugh one - uses context)
        ],
    },

    "sadness": {
        "keywords": [
            # English
            "sad", "sadly", "sadge", "depressed", "depressing",
            "cry", "crying", "cried", "tears", "tear",
            "sorry", "apologize", "apology", "forgive",
            "unfortunately", "heartbroken", "heartbreak",
            "miss you", "missing you", "i miss",
            "pain", "painful", "hurt", "hurts", "hurting",
            "disappointed", "disappointing", "letdown",
            "lonely", "alone", "hopeless", "helpless",
            "rip", "rest in peace", "condolences",
            # Emoticons
            "😢", "😭", "😿", "😞", "😔", "🥲", "😥",
            "💔", "🥀", "😩", "😫",
            # Tagalog/Filipino
            "lungkot", "malungkot", "nalulungkot",
            "iyak", "umiiyak", "naiyak",
            "saklap", "sakit", "masakit",
            "pighati", "kawawa", "kaawa",
            "sorry", "pasensya", "patawad",
            "miss na kita", "namimiss", "miss kita",
            "hirap", "mahirap", "nakakalungkot",
            "pagod", "pagod na", "nakakapagod",
            # Spanish
            "triste", "tristeza", "llorar", "llorando",
            "lo siento", "perdón", "dolor", "me duele",
            # French
            "triste", "tristesse", "pleurer", "désolé",
            "pardon", "douleur", "mal",
            # Japanese
            "悲しい", "泣く", "泣いた", "寂しい",
            "ごめん", "ごめんなさい", "辛い", "痛い",
            "残念", "しくしく", "えーん",
            # Korean
            "슬퍼", "슬프다", "울어", "울었어",
            "미안", "미안해", "죄송", "아프다",
            "ㅜㅜ", "ㅠㅠ", "ㅠ", "ㅜ",
            # Portuguese
            "triste", "chorar", "chorando", "desculpa",
            "saudade", "dor", "sofrer",
            # Indonesian/Malay
            "sedih", "menangis", "nangis", "maaf",
            "sakit", "kecewa",
            # German
            "traurig", "weinen", "tut mir leid", "schmerz",
            # Italian
            "triste", "piangere", "scusa", "scusami", "dolore",
            # Arabic
            "حزين", "أبكي", "آسف", "ألم",
            # Hindi
            "dukhi", "ro", "rona", "maafi",
            "dard", "taklif", "udaas",
            # Thai
            "เศร้า", "ร้องไห้", "เสียใจ", "ขอโทษ",
            # Vietnamese
            "buồn", "khóc", "xin lỗi", "đau",
            # Chinese
            "难过", "伤心", "哭", "对不起", "抱歉",
            # Cebuano
            "guol", "naguol", "hilak", "pasensya",
        ],
        "patterns": [
            r"ㅠ{2,}",               # Korean crying
            r"ㅜ{2,}",               # Korean crying
            r"T[_.]?T",              # T_T, T.T emoticon
            r";[\-_]?;",             # ;_; emoticon
        ],
    },

    "fire": {
        "keywords": [
            # English
            "fire", "lit", "sick", "insane", "dope", "epic",
            "game changer", "goated", "godly", "elite",
            "no cap", "bussin", "slaps", "hits different",
            "heat", "hype", "hyped", "gas", "peak",
            "top tier", "god tier", "next level", "OP",
            # Emoticons
            "🔥", "💥", "⚡", "🏆", "👑", "💪", "🦾",
            "🚀", "✨",
            # Tagalog/Filipino
            "apoy", "siga", "kalaban", "lethal",
            "ibang klase", "iba ka talaga", "sobrang galing",
            "grabe galing", "walang kupas", "walang tatalo",
            "ang lupit", "lupet mo", "ang lakas",
            "next level", "game changer",
            # Spanish
            "fuego", "bestial", "brutal", "épico", "potente",
            # French
            "feu", "ouf", "de ouf", "incroyable",
            # Japanese
            "神", "ヤバい", "最強", "天才", "鬼",
            "半端ない", "えぐい",
            # Korean
            "미쳤다", "개잘", "개쩔", "미친",
            "오지다", "쩐다",
            # Portuguese
            "brabo", "brabíssimo", "monstro", "insano",
            # Indonesian
            "gila", "gilak", "dewa", "parah",
        ],
        "patterns": [
            r"🔥{2,}",
            r"💪{2,}",
        ],
    },
}

# ============================================================
# NEGATION WORDS (Multi-language)
# These flip sentiment when they appear before an emotion keyword
# ============================================================
NEGATION_WORDS = {
    # English
    "not", "no", "never", "don't", "dont", "doesn't", "doesnt",
    "isn't", "isnt", "wasn't", "wasnt", "can't", "cant",
    "won't", "wont", "wouldn't", "wouldnt", "barely", "hardly",
    # Tagalog
    "hindi", "hinde", "hnd", "di", "wala", "walang",
    "ayaw", "ayoko", "wag", "huwag",
    # Spanish
    "no", "nunca", "jamás", "tampoco",
    # French
    "ne", "pas", "jamais", "rien",
    # Japanese
    "ない", "なし", "違う",
    # Korean
    "아니", "안", "못",
}

# ============================================================
# INTENSIFIER WORDS (boost confidence score)
# ============================================================
INTENSIFIERS = {
    # English
    "very", "really", "so", "super", "extremely", "absolutely",
    "totally", "completely", "incredibly", "insanely",
    "damn", "freaking", "fucking",
    # Tagalog
    "sobra", "sobrang", "napaka", "grabe", "grabeh",
    "ang", "ang hirap", "ang sakit", "ang galing",
    "ubod", "todo", "todo na",
    # Spanish
    "muy", "demasiado", "bastante", "súper",
    # French
    "très", "trop", "vraiment", "carrément",
    # Japanese
    "めっちゃ", "すごく", "超", "マジで", "本当に",
    # Korean
    "진짜", "완전", "너무", "엄청", "개",
}


def normalize_text(text: str) -> str:
    """
    Normalize text for matching:
    - Lowercase
    - Normalize unicode
    - Collapse repeated chars (e.g., "hahahaha" stays matchable)
    """
    text = text.lower().strip()
    text = unicodedata.normalize("NFC", text)
    return text


def analyze_message_emotion(message: str) -> tuple:
    """
    Analyze the emotional atmosphere of a message.
    
    Returns: (emotion_category: str | None, confidence: float, reaction_emoji: str | None)
    
    Confidence ranges from 0.0 to 1.0:
    - 0.0-0.3: Weak signal (no reaction)
    - 0.3-0.6: Moderate signal  
    - 0.6-1.0: Strong signal
    
    Only returns a reaction if confidence >= 0.3
    """
    if not message or not message.strip():
        return None, 0.0, None
    
    normalized = normalize_text(message)
    words = normalized.split()
    word_count = len(words)
    
    # Skip very short neutral messages (single letters, etc.)
    if word_count == 0:
        return None, 0.0, None
    
    # Score each emotion category
    scores = {}
    
    for emotion, data in LEXICON.items():
        score = 0.0
        keyword_hits = 0
        pattern_hits = 0
        
        # 1. Keyword matching (exact substring)
        for keyword in data["keywords"]:
            kw_lower = keyword.lower()
            if kw_lower in normalized:
                # Check for negation (look at word before the keyword)
                kw_pos = normalized.find(kw_lower)
                preceding_text = normalized[:kw_pos].strip().split()
                
                is_negated = False
                if preceding_text:
                    last_word = preceding_text[-1]
                    if last_word in NEGATION_WORDS:
                        is_negated = True
                
                if is_negated:
                    # Negated emotion - slightly reduce score
                    score -= 0.3
                else:
                    keyword_hits += 1
                    # Longer keyword = more specific = higher weight
                    kw_weight = min(1.0, len(kw_lower) / 5.0) * 0.5
                    score += 0.3 + kw_weight
        
        # 2. Regex pattern matching
        for pattern in data.get("patterns", []):
            try:
                matches = re.findall(pattern, normalized)
                if matches:
                    pattern_hits += len(matches)
                    score += 0.4 * len(matches)
            except re.error:
                pass
        
        # 3. Intensifier boost
        for intensifier in INTENSIFIERS:
            if intensifier in normalized:
                score *= 1.3
                break  # Only apply once
        
        # 4. Emoji density boost (messages with many emojis have stronger emotion)
        emoji_count = sum(1 for c in message if ord(c) > 0x1F600)
        if emoji_count > 0:
            score += 0.2 * min(emoji_count, 3)
        
        # 5. Exclamation/question mark intensity
        exclaim_count = message.count("!") + message.count("！")
        if exclaim_count > 0:
            score += 0.1 * min(exclaim_count, 3)
        
        # 6. ALL CAPS boost (shouting = stronger emotion)
        upper_ratio = sum(1 for c in message if c.isupper()) / max(len(message), 1)
        if upper_ratio > 0.5 and len(message) > 3:
            score += 0.3
        
        # Normalize score to 0-1 range
        if keyword_hits + pattern_hits > 0:
            # More hits = more confidence, but cap it
            confidence = min(1.0, score / max(1.0, word_count * 0.3))
            confidence = max(0.0, confidence)
            scores[emotion] = confidence
    
    if not scores:
        return None, 0.0, None
    
    # Pick the highest scoring emotion
    best_emotion = max(scores, key=scores.get)
    best_score = scores[best_emotion]
    
    # Threshold gate: only return reaction if confidence is meaningful
    if best_score < 0.25:
        return None, best_score, None
    
    # Resolve ties: if joy and love are close, prefer joy for "haha" type messages
    if "joy" in scores and "love" in scores:
        if abs(scores["joy"] - scores["love"]) < 0.1:
            # Check if the message has laugh patterns
            if any(kw in normalized for kw in ["haha", "hehe", "lol", "lmao", "😂", "🤣"]):
                best_emotion = "joy"
                best_score = scores["joy"]
    
    # Map to reaction emoji
    reaction = REACTION_MAP.get(best_emotion)
    
    return best_emotion, best_score, reaction


def get_reaction_for_message(message: str, has_attachments: bool = False) -> str | None:
    """
    High-level function: Given a message, return the appropriate reaction emoji or None.
    This is the main entry point for the auto-reaction system.
    """
    # Attachment shortcut: always react with ❤️ to files/images
    if has_attachments and (not message or len(message.strip()) < 5):
        return REACTION_MAP["attachment"]
    
    emotion, confidence, reaction = analyze_message_emotion(message)
    
    # If message has attachments AND emotion detected, use the emotion reaction
    if has_attachments and not reaction:
        return REACTION_MAP["attachment"]
    
    return reaction
