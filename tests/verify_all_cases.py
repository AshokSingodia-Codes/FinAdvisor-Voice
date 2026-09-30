"""
Verification script for all calculation and greeting test cases.
"""
import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from tools.fast_math import try_evaluate_fast_math
from core.greeting_handler import is_greeting_or_chitchat, get_greeting_response


def test_all_calculations():
    print("=== TESTING CALCULATION CASES ===")
    calc_cases = [
        ("2*4*8+150", 214.0),
        ("8/2", 4.0),
        ("4+4*2", 12.0),
        ("(4+4)*2", 16.0),
        ("2000892+3", 2000895.0),
        ("2*2", 4.0),
        ("17654487464+64465454", 17718952918.0),
        ("5% of 2020", 101.0),
        ("3/4 of 500", 375.0),
        ("what's a 20% discount on 1200", 960.0),
        ("what is two plus two", 4.0),
        ("multiply five by six", 30.0),
        ("₹50,000 + ₹12,000", 62000.0),
        ("$1,200 * 3", 3600.0),
        ("5 lakh + 2.5 lakh", 750000.0),
        ("average of 12%, 8%, 15%, -3%", 8.0),
        ("median of 500, 700, 300, 900", 600.0),
        ("calculate 12% of 50000, then add 8% of that result", 6480.0),
    ]

    for expr, expected in calc_cases:
        is_math, ans, val = try_evaluate_fast_math(expr)
        assert is_math is True, f"Failed match for {expr}"
        assert val == expected, f"Expected {expected}, got {val} for {expr}"
        print(f"  [PASS] '{expr}' => {val} (Output: {ans[:60]}...)")

    # Ratio test
    is_math, ans, _ = try_evaluate_fast_math("split 900 in a 2:3 ratio")
    assert is_math is True and "360" in ans and "540" in ans
    print("  [PASS] 'split 900 in a 2:3 ratio' => 360, 540")

    # Edge cases
    is_math, ans, val = try_evaluate_fast_math("8/0")
    assert is_math is True and "Division by zero" in ans
    print("  [PASS] '8/0' => Division by zero handled")

    is_math, ans, val = try_evaluate_fast_math("2+*3")
    assert is_math is False
    print("  [PASS] '2+*3' => Graceful fall-through")


def test_all_greetings():
    print("\n=== TESTING GREETING CASES ===")
    greet_cases = [
        # Cat A
        ("hi", "greeting"), ("hello", "greeting"), ("hey", "greeting"), ("good morning", "greeting"),
        ("good evening", "greeting"), ("yo", "greeting"),
        # Cat B
        ("how are you", "wellbeing"), ("how are you doing", "wellbeing"), ("what's up", "wellbeing"),
        ("how's it going", "wellbeing"), ("everything all right?", "wellbeing"), ("you good?", "wellbeing"),
        # Cat C
        ("bye", "parting"), ("goodbye", "parting"), ("see you", "parting"), ("see ya", "parting"),
        ("take care", "parting"), ("gtg", "parting"), ("catch you later", "parting"),
        # Cat D
        ("thanks", "gratitude"), ("thank you", "gratitude"), ("ok", "gratitude"), ("cool", "gratitude"),
        ("nice", "gratitude"), ("got it", "gratitude"), ("great", "gratitude"),
        # Cat E
        ("sorry", "apology"), ("my bad", "apology"), ("oops", "apology"), ("ignore that", "apology"),
        # Cat F
        ("who are you", "identity"), ("what are you", "identity"), ("are you a bot", "identity"),
        ("are you AI", "identity"), ("what can you do", "identity"), ("what is FinAdvisor-X", "identity"),
        # Cat G
        ("tell me a joke", "offtopic"), ("how's the weather", "offtopic"), ("do you like cricket", "offtopic"),
        # Cat H
        ("you're smart", "feedback_reaction"), ("you're useless", "feedback_reaction"),
        ("I hate you", "feedback_reaction"), ("you're wrong", "feedback_reaction"),
        # Cat I
        ("helo", "greeting"), ("hii", "greeting"), ("heyy", "greeting"), ("whatsup", "wellbeing"),
        ("howdy", "greeting"), ("sup", "wellbeing"), ("yow", "greeting"),

        # Cat J
        ("namaste", "greeting"), ("namaskar", "greeting"), ("kaise ho", "wellbeing"),
        ("kya haal hai", "wellbeing"), ("salaam", "greeting"), ("radhe radhe ji", "greeting"),
        # Cat K
        ("👋", "minimal_input"), ("🙂", "minimal_input"), ("...", "minimal_input"), ("?", "minimal_input"),
        # Cat N
        ("do you remember me", "meta_memory"), ("what did I ask before", "meta_memory"), ("do you save my data", "meta_memory"),
    ]

    for text, expected_cat in greet_cases:
        is_greet, cat = is_greeting_or_chitchat(text)
        assert is_greet is True, f"Failed greeting match for '{text}'"
        assert cat == expected_cat, f"Expected category '{expected_cat}', got '{cat}' for '{text}'"
        reply = get_greeting_response(cat, text)
        assert len(reply) > 15
        print(f"  [PASS] '{text}' => category='{cat}'")

    # Cat L: Compound queries MUST NOT BE SWALLOWED
    compound_queries = [
        "hi, what's Apple's stock price?",
        "hello! can you tell me Reliance's P/E ratio",
        "good morning, calculate tax on 15 lakh income under new regime",
        "ok, and what is the NPV at 8% discount rate?"
    ]
    for cq in compound_queries:
        is_greet, _ = is_greeting_or_chitchat(cq)
        assert is_greet is False, f"CRITICAL BUG: Compound query swallowed: {cq}"
        print(f"  [PASS] Compound query NOT swallowed: '{cq}'")


if __name__ == "__main__":
    test_all_calculations()
    test_all_greetings()
    print("\n✅ ALL CALCULATION AND GREETING TEST CASES PASSED 100%!")
