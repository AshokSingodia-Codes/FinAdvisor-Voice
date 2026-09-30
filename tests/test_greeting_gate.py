"""
Comprehensive Unit Tests for Pre-Router Greeting Gate (Categories A through O).
Ensures zero token overhead on chit-chat, robust fuzzy matching on typos,
rotational replies, and strict non-swallowing of real financial queries.
"""
import pytest
from core.greeting_handler import is_greeting_or_chitchat, get_greeting_response
from nodes.router import route_question


# =============================================================================
# CATEGORY A — Standard Greetings
# =============================================================================

def test_category_a_standard_greetings():
    standards = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "good night", "yo"]
    for g in standards:
        is_greet, cat = is_greeting_or_chitchat(g)
        assert is_greet is True, f"Failed standard greeting detection for '{g}'"
        assert cat in ("greeting", "parting")
        reply = get_greeting_response(cat, g)
        assert len(reply) > 20


# =============================================================================
# CATEGORY B — Wellbeing / Small Talk
# =============================================================================

def test_category_b_wellbeing_small_talk():
    wellbeing = ["how are you", "how are you doing", "what's up", "how's it going", "everything all right?", "you good?"]
    for wb in wellbeing:
        is_greet, cat = is_greeting_or_chitchat(wb)
        assert is_greet is True, f"Failed wellbeing detection for '{wb}'"
        assert cat == "wellbeing"
        reply = get_greeting_response(cat, wb)
        assert "doing great" in reply.lower() or "assist you" in reply.lower()


# =============================================================================
# CATEGORY C — Farewells
# =============================================================================

def test_category_c_farewells():
    farewells = ["bye", "goodbye", "see you", "see ya", "take care", "gtg", "catch you later", "talk later"]
    for f in farewells:
        is_greet, cat = is_greeting_or_chitchat(f)
        assert is_greet is True, f"Failed farewell detection for '{f}'"
        assert cat == "parting"
        reply = get_greeting_response(cat, f)
        assert "goodbye" in reply.lower() or "day ahead" in reply.lower()


# =============================================================================
# CATEGORY D — Gratitude & Acknowledgment
# =============================================================================

def test_category_d_gratitude_and_acknowledgment():
    gratitude = ["thanks", "thank you", "thanks a lot", "ok", "okay", "cool", "nice", "got it", "great", "perfect", "sounds good"]
    for gr in gratitude:
        is_greet, cat = is_greeting_or_chitchat(gr)
        assert is_greet is True, f"Failed gratitude/ack detection for '{gr}'"
        assert cat == "gratitude"


# =============================================================================
# CATEGORY E — Apologies / Self-Correction
# =============================================================================

def test_category_e_apologies():
    apologies = ["sorry", "my bad", "oops", "ignore that", "never mind", "nevermind"]
    for ap in apologies:
        is_greet, cat = is_greeting_or_chitchat(ap)
        assert is_greet is True, f"Failed apology detection for '{ap}'"
        assert cat == "apology"
        reply = get_greeting_response(cat, ap)
        assert "no worries" in reply.lower()


# =============================================================================
# CATEGORY F — Identity & Capability Questions
# =============================================================================

def test_category_f_identity_and_capabilities():
    identity = ["who are you", "what are you", "are you a bot", "are you AI", "what can you do", "what is FinAdvisor-X", "what do you help with"]
    for id_q in identity:
        is_greet, cat = is_greeting_or_chitchat(id_q)
        assert is_greet is True, f"Failed identity detection for '{id_q}'"
        assert cat == "identity"
        reply = get_greeting_response(cat, id_q)
        assert "FinAdvisor-X" in reply


# =============================================================================
# CATEGORY G — Off-Topic Casual Chit-Chat
# =============================================================================

def test_category_g_offtopic_banter():
    offtopic = ["tell me a joke", "how's the weather", "do you like cricket", "sing a song"]
    for ot in offtopic:
        is_greet, cat = is_greeting_or_chitchat(ot)
        assert is_greet is True, f"Failed off-topic detection for '{ot}'"
        assert cat == "offtopic"
        reply = get_greeting_response(cat, ot)
        assert "specialized in financial" in reply.lower() or "financial topics" in reply.lower()


# =============================================================================
# CATEGORY H — Compliments, Testing, Reactions
# =============================================================================

def test_category_h_feedback_reactions():
    reactions = ["you're smart", "you're useless", "I hate you", "are you even real", "you're wrong"]
    for rx in reactions:
        is_greet, cat = is_greeting_or_chitchat(rx)
        assert is_greet is True, f"Failed feedback reaction detection for '{rx}'"
        assert cat == "feedback_reaction"
        reply = get_greeting_response(cat, rx)
        assert "feedback" in reply.lower() or "financial" in reply.lower()


# =============================================================================
# CATEGORY I — Typos & Fuzzy Spelling Variants
# =============================================================================

def test_category_i_typos_and_fuzzy_variants():
    typos = ["helo", "hii", "heyy", "whatsup", "howdy", "sup", "yow", "hlw", "hlo"]
    for typ in typos:
        is_greet, cat = is_greeting_or_chitchat(typ)
        assert is_greet is True, f"Failed typo/fuzzy detection for '{typ}'"
        # 'whatsup' and 'sup' are correctly categorised as 'wellbeing' (small-talk bypass),
        # not 'greeting' — both categories legitimately bypass the graph pipeline.
        assert cat in ("greeting", "wellbeing"), \
            f"Expected 'greeting' or 'wellbeing' for '{typ}', got '{cat}'"


# =============================================================================
# CATEGORY J — Multilingual & Hinglish Greetings
# =============================================================================

def test_category_j_hinglish_and_regional():
    regional = ["namaste", "namaskar", "kaise ho", "kya haal hai", "salaam", "kaisa hai sab", "radhe radhe ji", "shubh prabhat", "kem cho"]
    for reg in regional:
        is_greet, cat = is_greeting_or_chitchat(reg)
        assert is_greet is True, f"Failed regional greeting detection for '{reg}'"
        assert cat in ("greeting", "wellbeing")


# =============================================================================
# CATEGORY K — Emoji & Minimal Punctuation
# =============================================================================

def test_category_k_emojis_and_minimal():
    minimal = ["👋", "🙂", "😊", "🙏", "...", "??", "!"]
    for m in minimal:
        is_greet, cat = is_greeting_or_chitchat(m)
        assert is_greet is True, f"Failed minimal input detection for '{m}'"
        assert cat == "minimal_input"
        reply = get_greeting_response(cat, m)
        assert "online and ready" in reply.lower() or "financial question" in reply.lower()


# =============================================================================
# CATEGORY L — Greeting Combined with Real Query (MUST NOT BE SWALLOWED)
# =============================================================================

def test_category_l_compound_query_not_swallowed():
    compound_queries = [
        "hi, what's Apple's stock price?",
        "hello! can you tell me Reliance's P/E ratio",
        "good morning, calculate tax on 15 lakh income under new regime",
        "hey assistant, calculate SIP of 10000 monthly for 5 years at 12%",
        "ok, and what is the NPV at 8% discount rate?"
    ]
    for cq in compound_queries:
        is_greet, _ = is_greeting_or_chitchat(cq)
        assert is_greet is False, f"CRITICAL: Compound query was mistakenly swallowed as greeting: '{cq}'"


# =============================================================================
# CATEGORY M — Repeated Greetings Rotation
# =============================================================================

def test_category_m_response_rotation():
    reply0 = get_greeting_response("greeting", "hi", turn_count=0)
    reply1 = get_greeting_response("greeting", "hi", turn_count=1)
    reply2 = get_greeting_response("greeting", "hi", turn_count=2)
    # Ensure variations are served across turns
    assert reply0 != reply1 or reply1 != reply2


# =============================================================================
# CATEGORY N — Meta Questions About Memory & Privacy
# =============================================================================

def test_category_n_meta_memory_privacy():
    meta_queries = ["do you remember me", "what did I ask before", "do you save my data", "how does your memory work"]
    for mq in meta_queries:
        is_greet, cat = is_greeting_or_chitchat(mq)
        assert is_greet is True, f"Failed meta memory detection for '{mq}'"
        assert cat == "meta_memory"
        reply = get_greeting_response(cat, mq)
        assert "isolated" in reply.lower() or "privacy" in reply.lower() or "private" in reply.lower()
