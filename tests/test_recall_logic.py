
import sys
import os
sys.path.append("/home/user/BANE_CORE")
from core import cortex_recall

def test_keywords():
    print("Testing School Keywords (Regex Word Boundary)...")
    tests = [
        ("pa check ng assignments", True),
        ("anong gawa mo?", True),
        ("nagagawa ko na ang project", True), # This should be FALSE now (whole word 'gawa' vs 'nagagawa')
        ("kailan ang deadline?", True),
        ("may holiday ba?", True),
    ]
    
    for msg, expected in tests:
        res = cortex_recall.handle_quota_mode("test_hash", msg)
        is_school = res and res.get("mode") == "school_fallback"
        # Since we might not have school data for 'test_hash', it might return None or something else
        # But we can check if it even tries to call the school helper
        print(f"Msg: '{msg}' -> Mode: {res['mode'] if res else 'None'}")

def test_similarity():
    print("\nTesting Smart Recall Threshold...")
    # Mocking some data would be better but let's just check the thresholds
    msg1 = "Kamusta"
    msg2 = "Kamusta ang school?"
    from difflib import SequenceMatcher
    import re
    a_clean = re.sub(r'[^\w\s]', '', msg1.lower().strip())
    b_clean = re.sub(r'[^\w\s]', '', msg2.lower().strip())
    ratio = SequenceMatcher(None, a_clean, b_clean).ratio()
    print(f"Similarity '{msg1}' vs '{msg2}': {ratio:.2f} (Threshold is now 0.8)")

if __name__ == "__main__":
    test_keywords()
    test_similarity()
