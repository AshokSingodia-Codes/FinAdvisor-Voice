import pytest
from core.greeting_handler import is_greeting_or_chitchat, get_greeting_response
from nodes.router import route_question
from nodes.evidence_builder import build_evidence

def test_greeting_variations():
    variations = [
        # Single token & casual
        "hi", "hello", "hey", "yo", "sup", "hola", "aloha", "howdy", "ciao",
        "hlo", "hlw", "helo", "hie", "gm", "gn", "oye",
        # Elongated / stretched tokens
        "heyyyyy", "hiiiii", "helloooo", "yoooo", "suuup", "namasteeee", "holaaa",
        # Emojis & Punctuation
        "👋", "🙏", "🤝", "hello!", "hey...", "??", "...",
        # Compound & friendly suffix
        "hello!", "hey there", "hi there", "hey assistant", "hello finadvisor",
        "hey bot", "hi bro", "hello dost", "hey buddy", "good morning sir",
        "gud morning", "shubh prabhat team", "radhe radhe ji",
        # Indian / Regional greetings
        "namaste", "namaskar", "namaskaram", "namaskara", "pranam", "pranaam", "ram ram", "radhe radhe",
        "jai shree ram", "jai shri krishna", "jai jinendra", "har har mahadev", "vanakkam",
        "kem cho", "kemcho", "khemcho", "salaam", "assalam alaikum", "adaab", "sat sri akal", "shubh prabhat",
        # Liveness / System Ping
        "are you there", "u there", "are you alive", "alive", "ping", "test", "testing", "can you hear me",
        # Wellbeing / Check-in
        "how are you", "how are you doing", "how r u", "kya haal hai", "kaise ho", "sab theek", "sab badhiya",
        # Identity / Capability
        "who are you", "what can you do", "aap kaun ho", "apna parichay do", "what is your name",
        # Help & Menu
        "help", "menu", "options", "madad", "help chahiye", "guide me",
        # Gratitude & Parting
        "thank you", "thanks", "thx", "ty", "tysm", "shukriya", "dhanyawad",
        "bye", "goodbye", "see you", "tata", "alvida", "chal bye", "good night"
    ]
    
    for v in variations:
        is_greet, cat = is_greeting_or_chitchat(v)
        assert is_greet is True, f"Failed greeting detection for: '{v}'"
        assert cat is not None, f"No category assigned for: '{v}'"
        reply = get_greeting_response(cat, v)
        assert len(reply) > 20, f"Empty or too short reply for: '{v}'"


def test_finance_queries_not_mistaken_for_greetings():
    finance_queries = [
        "Hi, what is the tax on 15 lakh income under new regime?",
        "Hello, calculate my SIP for 10000 monthly for 5 years at 12%",
        "Hey, what is the stock price of Reliance?",
        "Good morning, compute EMI on 50 lakh loan for 20 years at 8.5%",
        "What is the capital gains tax on equity mutual funds?"
    ]
    
    for fq in finance_queries:
        is_greet, _ = is_greeting_or_chitchat(fq)
        assert is_greet is False, f"Finance query was mistakenly classified as greeting: '{fq}'"


def test_router_fast_path_for_greetings():
    state = {"original_question": "hello there!", "memory_context": ""}
    res = route_question(state)
    assert res["routing_decision"] == "direct_answer"
    assert res["depth"] == "quick"


def test_evidence_builder_instant_reply_for_greetings():
    state = {
        "original_question": "namaste finadvisor",
        "memory_context": "",
        "document_id": None,
        "retrieved_context": []
    }
    res = build_evidence(state)
    assert "FinAdvisor-X" in res["final_answer"]

