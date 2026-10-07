"""
Unified Pre-Router Greeting & Chit-Chat Gate for FinAdvisor.
Deterministically classifies and responds to Categories A through N without LLM calls.
Guarantees zero token overhead and never swallows compound queries (Category L).
"""
import re
from typing import Tuple, Optional, List, Dict, Any

# -----------------------------------------------------------------------------
# CATEGORY TOKEN & PHRASE SETS
# -----------------------------------------------------------------------------

EMOJI_GREETINGS = {"👋", "🙏", "🤝", "🙌", "😊", "😃", "🙂", "🙋‍♂️", "🙋‍♀️", "🙋", "✨"}

GREETING_TOKENS = {
    # English & Casual (Category A & I)
    "hi", "hello", "hey", "heyy", "heyyy", "heya", "hiya", "howdy", "hola", "aloha", "bonjour", "ciao",
    "yo", "greetings", "salutations", "morning", "afternoon", "evening", "gm", "gn", "ga", "ge", "gday", "g'day",
    "hlo", "hlw", "helo", "heloo", "helllo", "hie", "hiee", "oye", "oi", "yow",
    # Hindi / Hinglish / Regional Indian (Category J)
    "namaste", "namaskar", "namaskaram", "namaskara", "pranam", "pranaam", "charansparsh", "vanakkam",
    "kemcho", "kem cho", "khemcho", "ram ram", "radhe radhe", "jai shree ram", "jai shri krishna",
    "jai jinendra", "jai mata di", "har har mahadev", "salaam", "salam", "assalam alaikum", "assalamu alaikum",
    "walekum assalam", "adaab", "adab", "sat sri akal", "sasrikaal", "shubh prabhat", "suprabhat",
    "shubh sandhya", "shubh ratri", "khammaghani", "khamma ghani"
}

GREETING_PREFIXES = {
    "hi", "hello", "hey", "heyy", "hiya", "howdy", "hola", "namaste", "namaskar",
    "good morning", "good afternoon", "good evening", "good day", "greetings", "shubh prabhat",
    "suprabhat", "gud morning", "gud mrng", "gud evening", "gud evng"
}

GREETING_SUFFIXES = {
    "there", "assistant", "finadvisor", "advisor", "bot", "ai", "sir", "mam",
    "maam", "friend", "buddy", "bro", "dude", "team", "everyone", "all", "ji",
    "bhai", "yaar", "saab", "sahab", "dost", "boss", "champ", "fellow", "folks"
}

# CATEGORY B: Wellbeing / Small Talk
WELLBEING_PHRASES = {
    "how are you", "how are you doing", "how r u", "how do you do", "how is it going",
    "hows it going", "how's it going", "how are things", "how is everything",
    "hows everything", "hope you are doing well", "how have you been", "how is your day",
    "hows life", "how is life", "kya haal hai", "kya haal", "kaise ho", "kaisa hai",
    "kya chal raha hai", "kaisa chal raha hai", "sab theek", "sab theek hai", "sab badhiya",
    "sab badiya", "all good", "everything good", "all well", "you good", "you good?",
    "everything all right", "everything all right?", "all right?", "whats up", "what's up",
    "what up", "wassup", "wazzup", "whatsup", "sup",
    # Presence / liveness check phrases
    "are you there", "u there", "you there", "you still there", "hello are you there",
    "anyone there", "you online", "you alive", "are you alive", "alive", "ping", "test", "testing",
    "can you hear me", "you awake",
}



# CATEGORY C: Farewells
PARTING_PHRASES = {
    "bye", "goodbye", "cya", "see you", "see ya", "take care", "gtg", "catch you later",
    "talk later", "talk to you later", "have a nice day", "good night", "bye bye", "alvida",
    "phir milenge", "tata", "tata bye bye", "chal bye"
}

# CATEGORY D: Gratitude & Acknowledgment
GRATITUDE_PHRASES = {
    "thanks", "thank you", "thanks a lot", "thank you so much", "thx", "ty", "tysm", "tyvm",
    "appreciate it", "great thanks", "many thanks", "thank u", "awesome thanks", "thnx", "thanx",
    "dhanyawad", "dhanyavad", "shukriya", "bohot shukriya", "bahut shukriya"
}

STANDALONE_ACKS = {
    "ok", "okay", "cool", "nice", "got it", "great", "perfect", "sounds good",
    "roger that", "k", "kk", "noted", "understood", "fine", "alright", "all right"
}

# CATEGORY E: Apologies / Self-Correction
APOLOGY_PHRASES = {
    "sorry", "my bad", "oops", "ignore that", "never mind", "nevermind", "disregard that",
    "scratch that", "my mistake", "galti ho gayi", "ignore previous"
}

# CATEGORY F: Identity & Capability Questions / Help Menu
IDENTITY_PHRASES = {
    "who are you", "what are you", "are you a bot", "are you ai", "are you an ai",
    "what can you do", "what is finadvisor", "what is finadvisor-x", "what do you help with",
    "who made you", "what is your name", "what's your name", "whats your name",
    "tell me about yourself", "introduce yourself", "who built you", "who created you",
    "aap kaun ho", "tum kaun ho", "tera naam kya hai", "apna naam batao", "apna parichay do",
    "help", "menu", "options", "madad", "help chahiye", "guide me",
    "what are your capabilities", "capabilities", "what are your features", "features",
    "what can you help me with", "how can you assist", "how can you help",
    "what services do you offer", "what are your capabilities as a financial advisor"
}

# CATEGORY G: Off-topic Casual Banter
OFFTOPIC_PHRASES = {
    "tell me a joke", "make me laugh", "how is the weather", "hows the weather", "how's the weather",
    "do you like cricket", "who won the match", "what is the weather", "sing a song",
    "what is your favorite color", "whats your favorite color", "do you have feelings"
}

# CATEGORY H: Compliments, Testing, Mild Hostility
FEEDBACK_TEST_PHRASES = {
    "you are smart", "youre smart", "you are awesome", "youre awesome", "good job", "well done",
    "you are useless", "youre useless", "i hate you", "are you even real", "you are wrong",
    "youre wrong", "you are dumb", "youre dumb", "bad bot", "stupid bot", "are you stupid"
}


# CATEGORY N: Meta Memory & Privacy Questions
META_MEMORY_PHRASES = {
    "do you remember me", "what did i ask before", "do you save my data", "how does your memory work",
    "do you remember our chat", "what do you know about me", "is my data safe", "is my data private",
    "do you store my files", "where is my data stored"
}

# Substantive finance indicator keywords: if any of these are present along with multiple words,
# it is NEVER a pure greeting (prevents swallowing Category L)
FINANCE_INDICATORS = {
    "tax", "taxes", "gst", "itr", "slab", "regime", "deduction", "80c", "87a",
    "stock", "stocks", "share", "shares", "price", "quote", "nifty", "sensex",
    "reliance", "tcs", "hdfc", "infosys", "itc", "apple", "aapl", "nvda", "msft",
    "sip", "cagr", "emi", "wacc", "npv", "dcf", "irr", "roe", "pe", "p/e", "ratio",
    "calculate", "computation", "compute", "formula", "interest", "compounding",
    "salary", "income", "expense", "expenses", "budget", "portfolio", "investment",
    "mutual fund", "mf", "nav", "dividend", "balance sheet", "p&l", "revenue",
    "profit", "ebitda", "capital gain", "ltcg", "stcg", "loan", "debt", "cibil",
    "fd", "fixed deposit", "return", "returns", "yield", "growth", "margin"
}


# -----------------------------------------------------------------------------
# NORMALIZATION & MATCHING HELPERS
# -----------------------------------------------------------------------------

def normalize_text(text: str) -> str:
    """Strip punctuation and extra whitespace, convert to lowercase, stripping apostrophes cleanly."""
    if not text:
        return ""
    # Strip apostrophes cleanly so 'what's' -> 'whats', 'you're' -> 'youre'
    cleaned = text.lower().replace("'", "").replace("’", "")
    cleaned = re.sub(r"[^\w\s₹$€%]", " ", cleaned)
    return " ".join(cleaned.split())



def collapse_repeated_characters(token: str) -> str:
    """Collapses elongated words like 'heyyyyy' -> 'hey', 'hiiiii' -> 'hi', 'helloooo' -> 'hello'."""
    collapsed = re.sub(r'(.)\1{2,}', r'\1', token)
    return collapsed


def _levenshtein_distance(s1: str, s2: str) -> int:
    """Computes basic Levenshtein distance for fuzzy typo matching (Category I)."""
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    prev_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row
    return prev_row[-1]


def is_fuzzy_token_match(word: str, token_set: set, max_dist: int = 1) -> bool:
    """Checks if a word fuzzy-matches any token in the token set within edit distance."""
    if word in token_set:
        return True
    collapsed = collapse_repeated_characters(word)
    if collapsed in token_set:
        return True
    if len(word) >= 4:
        for t in token_set:
            if abs(len(t) - len(word)) <= max_dist:
                if _levenshtein_distance(word, t) <= max_dist:
                    return True
    return False


# -----------------------------------------------------------------------------
# PRE-ROUTER GATE: is_greeting_or_chitchat
# -----------------------------------------------------------------------------

def is_greeting_or_chitchat(raw_text: str) -> Tuple[bool, Optional[str]]:
    """
    Unified pre-router gate checking Categories A through N.
    Returns:
        (is_greeting, category)
    
    Categories:
        'greeting', 'wellbeing', 'parting', 'gratitude', 'apology', 'identity',
        'offtopic', 'feedback_reaction', 'meta_memory', 'minimal_input'
    """
    if not raw_text:
        return False, None

    stripped = raw_text.strip()
    if not stripped:
        return True, "minimal_input"

    # CATEGORY K: Emoji-only or punctuation-only minimal input
    if any(emoji in stripped for emoji in EMOJI_GREETINGS) and len(stripped) <= 6:
        return True, "minimal_input"

    norm = normalize_text(stripped)
    if not norm:
        # Lone punctuation like '??', '...', '!'
        return True, "minimal_input"

    words = norm.split()

    # CATEGORY L: Compound Greeting + Real Financial Query
    # If query contains substantive finance keywords or numbers AND has content words,
    # NEVER swallow as a greeting. Let it route to financial solver/retriever.
    has_finance_keyword = any(kw in norm for kw in FINANCE_INDICATORS)
    has_digits = any(char.isdigit() for char in norm)

    if (has_finance_keyword or has_digits) and len(words) >= 2:
        return False, None

    # CATEGORY D: Standalone Acknowledgment (ok, cool, got it, etc.)
    # ONLY match if it is the standalone message
    if norm in STANDALONE_ACKS:
        return True, "gratitude"

    # CATEGORY E: Apologies / Self-Correction
    if norm in APOLOGY_PHRASES or any(norm.startswith(p) for p in ("sorry", "my bad", "oops", "ignore that")):
        if len(words) <= 5 and not has_finance_keyword:
            return True, "apology"

    # CATEGORY C: Farewells
    if norm in PARTING_PHRASES or any(norm.startswith(p) for p in ("bye ", "goodbye ", "tata ", "cya ")):
        return True, "parting"
    if any(p in norm for p in ("see you", "see ya", "talk to you later", "good night", "phir milenge", "alvida", "take care", "gtg", "talk later")):
        if len(words) <= 6 and not has_finance_keyword:
            return True, "parting"

    # CATEGORY D: Gratitude
    if norm in GRATITUDE_PHRASES or any(norm.startswith(g) for g in ("thank you", "thanks ", "shukriya", "dhanyawad")):
        return True, "gratitude"
    if any(g in norm for g in ("thank you", "thanks a lot", "appreciate it", "bohot shukriya", "thank u")):
        if len(words) <= 6 and not has_finance_keyword:
            return True, "gratitude"

    # CATEGORY N: Meta Memory & Privacy Questions
    if norm in META_MEMORY_PHRASES or any(p in norm for p in ("remember me", "save my data", "memory work", "is my data safe", "remember our chat")):
        if len(words) <= 8 and not has_finance_keyword:
            return True, "meta_memory"

    # CATEGORY F: Identity & Capabilities
    if norm in IDENTITY_PHRASES or any(p in norm for p in ("who are you", "what can you do", "what are your capabilities", "capabilities as a financial advisor", "are you a bot", "are you ai", "what is finadvisor", "aap kaun ho", "tum kaun ho")):
        if len(words) <= 14:
            return True, "identity"

    # CATEGORY G: Off-topic casual banter
    if norm in OFFTOPIC_PHRASES or any(p in norm for p in ("tell me a joke", "how is the weather", "hows the weather", "like cricket", "sing a song")):
        if len(words) <= 8 and not has_finance_keyword:
            return True, "offtopic"

    # CATEGORY H: Feedback / Testing / Reaction
    if norm in FEEDBACK_TEST_PHRASES or any(p in norm for p in ("you are smart", "youre smart", "you are useless", "youre useless", "hate you", "are you even real", "you are wrong", "youre wrong")):
        if len(words) <= 6 and not has_finance_keyword:
            return True, "feedback_reaction"


    # CATEGORY B: Wellbeing / Small Talk
    if norm in WELLBEING_PHRASES or any(phrase in norm for phrase in ("how are you", "how r u", "how is it going", "hows it going", "how do you do", "kya haal", "kaise ho", "kaisa hai", "kya chal raha", "sab theek", "sab badhiya", "you good", "all right", "whats up", "whatsup", "wassup", "sup")):
        if len(words) <= 7 and not has_finance_keyword:
            return True, "wellbeing"


    # CATEGORY A & J & I: Exact, Suffix & Fuzzy Greeting Match
    if norm in GREETING_TOKENS:
        return True, "greeting"

    # Multi-word phrase matching with suffixes (e.g. "radhe radhe ji", "good morning team")
    for phrase in sorted(GREETING_TOKENS, key=len, reverse=True):
        if phrase in norm:
            rem_str = norm.replace(phrase, " ").strip()
            rem_words = rem_str.split()
            if not rem_words or all(w in GREETING_SUFFIXES or w in GREETING_TOKENS or len(w) <= 2 for w in rem_words):
                return True, "greeting"

    # Token-Level Evaluation with Typos / Fuzzy Match (Category I)
    for w in words:
        if is_fuzzy_token_match(w, GREETING_TOKENS):
            remainder = [token for token in words if token != w and not is_fuzzy_token_match(token, GREETING_TOKENS)]
            if not remainder or all(r in GREETING_SUFFIXES or is_fuzzy_token_match(r, GREETING_TOKENS) or len(r) <= 2 for r in remainder):
                return True, "greeting"

    # Multi-token combinations: "good morning sir", "gud evening friend"
    if len(words) <= 5:
        first_word = words[0]
        first_two = " ".join(words[:2]) if len(words) >= 2 else ""
        if is_fuzzy_token_match(first_word, GREETING_TOKENS) or first_two in GREETING_PREFIXES:
            remainder = words[1:] if is_fuzzy_token_match(first_word, GREETING_TOKENS) else words[2:]
            if not remainder or all(w in GREETING_SUFFIXES or is_fuzzy_token_match(w, GREETING_TOKENS) for w in remainder):
                return True, "greeting"

    # Single word fallback
    if len(words) == 1:
        single = collapse_repeated_characters(words[0])
        if single in {"thanks", "thankyou", "thx", "ty", "tysm", "shukriya", "dhanyawad"}:
            return True, "gratitude"
        if single in {"bye", "goodbye", "cya", "tata", "alvida"}:
            return True, "parting"
        if single in {"hi", "hey", "hie", "yo", "sup", "hlo", "hlw", "helo", "radhe", "ram", "oye", "yow"}:
            return True, "greeting"

    return False, None


# -----------------------------------------------------------------------------
# CATEGORY M: RESPONSE ROTATION & CANNED TEMPLATES
# -----------------------------------------------------------------------------

_GREETING_ROTATIONS = [
    (
        "Hello! 👋 I am **FinAdvisor-X**, your AI Financial Intelligence Assistant.\n\n"
        "How can I assist you today? You can ask me about:\n"
        "* 📈 **Market Intelligence**: Live equity quotes from NSE/BSE and fundamental valuation.\n"
        "* 🧮 **Financial Calculations**: SIP compounding, WACC, DCF valuation, CAGR, and loan EMI.\n"
        "* 🏛️ **Indian Tax Planning**: FY 2026-27 New vs Old Tax Regime calculations and standard deductions.\n"
        "* 📄 **Document Analysis**: Upload PDF salary slips or financial statements for private analysis."
    ),
    (
        "Hello again! 👋 Ready to explore the markets or run financial models.\n\n"
        "What numbers or tickers would you like to calculate today? Feel free to ask for a stock quote, SIP forecast, or tax breakdown."
    ),
    (
        "Welcome back! ⚡ FinAdvisor-X is active and connected to real-time market data.\n\n"
        "Need a calculation (SIP/CAGR/Loan EMI) or equity intelligence? Let me know how I can help!"
    )
]


def get_greeting_response(category: str, query: str = "", turn_count: int = 0) -> str:
    """
    Returns a rich, tailored instant response for chit-chat categories.
    Rotates greetings (Category M) based on turn_count.
    """
    if category == "wellbeing":
        return (
            "I'm doing great and ready to assist you! 🚀\n\n"
            "How can I help you with your financial journey today? You can ask me about:\n"
            "* 🧮 **Calculations**: *'SIP of ₹10,000 for 10 years at 12%'* or *'EMI on 50L home loan'*\n"
            "* 🏛️ **Tax Planning**: *'Tax on ₹15 Lakh income under new regime FY 2026-27'*\n"
            "* 📈 **Stock & Market Intelligence**: *'Reliance live price'* or *'TCS fundamentals'*\n"
            "* 📄 **Document Analysis**: Attach salary slips or bank statements for private analysis."
        )

    if category == "identity":
        return (
            "Hello! 👋 I am **FinAdvisor-X**, your AI Financial Intelligence Assistant.\n\n"
            "I specialize in deterministic financial modeling, real-time equity analytics, Indian tax optimization (FY 2026-27), and private document evaluation.\n\n"
            "**Core Capabilities**:\n"
            "1. **🧮 Financial Modeling**: Compound interest, SIP, CAGR, loan EMI, DCF valuation, and capital gains.\n"
            "2. **🏛️ Indian Tax Optimization**: Income tax slab breakdown, standard deduction, and Section 87A rebate computation.\n"
            "3. **📈 Live Market Intelligence**: Live equity quotes from NSE/BSE and global tickers.\n"
            "4. **📄 Isolated Document Ingestion**: Upload PDF bank statements or salary slips for isolated session analysis."
        )

    if category == "apology":
        return "No worries at all! 😊 How can I assist you with your financial questions or calculations?"

    if category == "offtopic":
        return (
            "I'm specialized in financial intelligence, equity analytics, and tax planning! 📊\n\n"
            "While I'm focused on financial topics rather than general trivia or jokes, I'd love to help you analyze stock fundamentals, calculate investment returns, or compare tax regimes. What financial question can I solve for you?"
        )

    if category == "feedback_reaction":
        return (
            "Thank you for the feedback! I'm constantly calibrated to provide verified, deterministic financial data. Let me know what financial calculation or market update you need assistance with!"
        )

    if category == "meta_memory":
        return (
            "🔒 **FinAdvisor-X Privacy & Memory Architecture**\n\n"
            "1. **Isolated Session Memory**: Your conversation history and uploaded documents are strictly private and isolated to your account session.\n"
            "2. **No Third-Party Model Training**: Your personal numbers, salary slips, and financial statements are never shared or used to train external models.\n"
            "3. **User Control**: You can clear or delete your conversation history at any time using the conversation options in the sidebar."
        )

    if category == "minimal_input":
        return (
            "Hello! 👋 I am online and ready to assist you. Ask any financial question, stock ticker, or calculation to get started!"
        )

    if category == "gratitude":
        return (
            "You're very welcome! 😊 Feel free to ask whenever you need more financial calculations, market updates, or tax planning. Have a great day!"
        )

    if category == "parting":
        return (
            "Goodbye! 👋 Have a wonderful day ahead, and make smart financial decisions! I'll be here whenever you need assistance."
        )

    # Standard Greeting (Category A / J / I with Category M Rotation)
    idx = turn_count % len(_GREETING_ROTATIONS)
    return _GREETING_ROTATIONS[idx]
