import re
import time
import json
from typing import Dict, Tuple, Optional, Any
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from graph.state import AgentState
from core.db import fast_chat, get_structured_fast_chat
from core.greeting_handler import is_greeting_or_chitchat
from tools.fast_math import try_evaluate_fast_math
from core.memory import get_conversation_continuity, save_conversation_continuity

# 10-Minute TTL Cache for identical router queries
_ROUTER_CACHE: Dict[str, Tuple[str, str, float]] = {}
_ROUTER_CACHE_TTL = 600  # 10 minutes

# trigger word/phrase sets used as fast-path pre-classification
# before falling back to LLM classification for ambiguous queries

QUICK_TRIGGERS = {
    "quick", "quickly", "just tell me", "just the number", "in one line",
    "one liner", "briefly", "short answer", "just answer", "no explanation",
    "straight answer", "cut to the chase", "just the fact", "simple answer",
    "yes or no", "direct answer", "just say", "in a word", "one word answer",
}

SUMMARY_TRIGGERS = {
    "summary", "summarize", "summarise", "recap", "brief", "overview",
    "tl;dr", "tldr", "in a nutshell", "in short", "gist", "synopsis",
    "rundown", "wrap up", "wrap-up", "cliffnotes", "cliff notes",
    "key takeaways", "key points", "highlights", "bullet points",
    "bullet summary", "quick take", "main points", "top points",
    "condense", "boil it down", "give me the highlights",
}

DEEP_TRIGGERS = {
    "deep dive", "deepdive", "in detail", "in-depth", "indepth", "elaborate",
    "comprehensive", "detailed breakdown", "explain fully", "explain in detail",
    "step by step", "step-by-step analysis", "thorough explanation",
    "break down completely", "exhaustively", "full breakdown", "walk me through",
    "explain thoroughly", "give me everything", "all the details",
    "complete analysis", "full analysis", "detailed analysis",
    "with formulas", "show your work", "show the math", "explain the reasoning",
}

ESCALATE_TRIGGERS = {
    "go deeper", "explain more", "elaborate on that", "more detail",
    "tell me more", "expand on that", "dig deeper", "more info",
    "can you elaborate", "explain that more", "give me more detail",
    "what else", "go on", "continue", "more on this",
}

DEESCALATE_TRIGGERS = {
    "just the summary", "too long", "shorter please", "keep it short",
    "tldr this", "simplify", "in simple terms", "make it brief",
    "less detail", "cut it down", "shorten this",
}

def classify_depth(question: str) -> str:
    """Classify user question depth into 'quick' | 'summary' | 'deep'."""
    lower_q = (question or "").lower()
    if any(trigger in lower_q for trigger in DEESCALATE_TRIGGERS) or any(trigger in lower_q for trigger in QUICK_TRIGGERS):
        return "quick"
    if any(trigger in lower_q for trigger in ESCALATE_TRIGGERS) or any(trigger in lower_q for trigger in DEEP_TRIGGERS):
        return "deep"
    if any(trigger in lower_q for trigger in SUMMARY_TRIGGERS):
        return "summary"
    return "quick"

class Route(BaseModel):
    decision: str = Field(
        description="The routing decision. Must be one of: 'decompose', 'hybrid_search', 'financial_table', 'calculation', 'math_calculation', 'direct_answer', 'live_market_data', 'current_events'"
    )
    resolved_query: Optional[str] = Field(
        default=None,
        description="Rewrite the question into a complete, standalone question resolving any anaphoric pronouns or implicit references (e.g. 'its P/E', 'show its revenue', 'and this one') using active entities. If already self-contained, repeat the question."
    )
    is_topic_change: bool = Field(
        default=False,
        description="Set to true if the question is genuinely unrelated to the active entities/topic and shifts to a new subject (e.g., asking about compound interest or general math after discussing Reliance). When true, old entities will be reset."
    )
    extracted_entities: Dict[str, Optional[str]] = Field(
        default_factory=dict,
        description="Entities mentioned or updated: 'company', 'ticker', 'mutual_fund', 'metric'."
    )
    conversation_topic: Optional[str] = Field(
        default=None,
        description="A short 2-5 word summary of the active conversation thread (e.g., 'Reliance Financials', 'Compound Interest', 'SIP Return')."
    )

router_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert financial routing and conversational continuity assistant.
Analyze the user question along with recent conversation history and active entities.
Perform routing, pronoun/follow-up resolution, entity tracking, and topic shift detection in a SINGLE pass.

ROUTING DECISIONS:
- 'decompose': comparing multiple distinct entities or multi-part complex queries.
- 'math_calculation': basic arithmetic (+ - * / % ^).
- 'calculation': computes a financial formula with given numbers (WACC, CAGR, SIP, NPV, DCF, loan EMI, compounding, capital gains tax).
- 'hybrid_search': concept definitions, statutory tax limits/acts (Section 80C, Budget 2024 capital gains, LTCG/STCG provisions, tax exemption limits), regulatory bulletins/directives, 10-K disclosures, corporate filings, or personal documents. NOTE: Statutory tax rules and enacted budgets (such as Budget 2024) belong in hybrid_search, NOT current_events.
- 'financial_table': tabular data (balance sheet, income statement).
- 'live_market_data': live stock prices, Indian tickers (Reliance, TCS, NIFTY 50), or market status.
- 'current_events': questions about breaking live news (today, this week, breaking repo rate announcements). Do NOT route statutory tax laws, enacted budgets (like Budget 2024), or general tax limits here.
- 'direct_answer': greeting, advice, personal memory query, or chit-chat.

CONTINUITY & PRONOUN RESOLUTION RULES:
1. 'resolved_query':
   - If the user uses pronouns or implicit references ('what about its P/E', 'show its revenue', 'and this one's return', 'what about TCS instead'), resolve it to a full standalone question using the active entities.
   - If the question is already complete and self-contained, or is an unrelated topic change, output the original question unchanged.
2. 'is_topic_change':
   - Set to TRUE if the question is genuinely unrelated to the active entities/topic (e.g., asking about compound interest or mutual funds after discussing a specific company like Reliance).
   - Set to FALSE if the user is asking a follow-up or staying on the same subject.
3. 'extracted_entities':
   - Extract any explicit company name ('company'), ticker ('ticker'), mutual fund scheme ('mutual_fund'), or metric ('metric') mentioned in the question.
4. 'conversation_topic':
   - Provide a short 2-5 word description of the active topic thread.
"""),
    ("human", """Active Entities: {active_entities}
Current Topic: {conversation_topic}

Recent Conversation:
{memory_context}

User Question: {question}""")
])

router_chain = router_prompt | get_structured_fast_chat(Route)

def format_history_for_router(history, max_turns=4):
    if not history:
        return "None (First interaction)"
    formatted = []
    for msg in history[-max_turns:]:
        role = "User" if msg.get("role") == "user" else "Assistant"
        content = msg.get("content", "").strip()
        if len(content) > 250:
            content = content[:250] + "..."
        formatted.append(f"{role}: {content}")
    return "\n".join(formatted)

def route_question(state: AgentState):
    print("---NODE: ROUTER---")
    question = state.get("original_question", "")
    # Preserve the raw memory_context; if it's explicitly an empty string we should keep it that way.
    memory_context = state.get("memory_context")  # May be None or ""
    if memory_context is None:
        # No explicit memory_context supplied – fall back to formatted chat history.
        memory_context = format_history_for_router(state.get("chat_history", []))
    document_id = state.get("document_id")
    conv_id = state.get("conversation_id", "")
    user_id = state.get("user_id", "")
    lower = question.strip().lower()

    depth = classify_depth(question)

    # Load active conversation continuity from state or persistent store
    active_entities = state.get("active_entities")
    conversation_topic = state.get("conversation_topic")
    if active_entities is None or conversation_topic is None:
        continuity = get_conversation_continuity(conv_id, user_id=user_id) if conv_id else {}
        if active_entities is None:
            active_entities = continuity.get("active_entities") or {}
        if conversation_topic is None:
            conversation_topic = continuity.get("conversation_topic") or ""

    # --- Fast-Path 1: Instant Personal Document Route (<1ms) ---
    if document_id:
        has_digits = any(char.isdigit() for char in lower)
        is_explicit_math = has_digits and any(term in lower for term in ["add", "subtract", "multiply", "divide", "plus", "minus", "sum", "total", "cagr", "sip", "wacc", "npv", "dcf", "emi"])
        if not is_explicit_math:
            print("  [Router: FAST-PATH PERSONAL DOC] -> 'hybrid_search'")
            return {
                "routing_decision": "hybrid_search",
                "current_question": question,
                "resolved_query": question,
                "active_entities": active_entities,
                "conversation_topic": conversation_topic,
                "depth": depth
            }

    # --- Fast-Path 2: Instant Greetings / Casual Chit-Chat (<1ms) ---
    is_greeting, category = is_greeting_or_chitchat(question)
    if is_greeting and not document_id:
        from core.greeting_handler import get_greeting_response
        instant_reply = get_greeting_response(category or "greeting", question)
        print(f"  [Router: FAST-PATH GREETING/CHIT-CHAT] category='{category}' -> 'direct_answer'")
        return {
            "routing_decision": "direct_answer",
            "current_question": question,
            "resolved_query": question,
            "active_entities": active_entities,
            "conversation_topic": conversation_topic or "Greeting",
            "depth": "quick",
            "draft_answer": instant_reply,
            "final_answer": instant_reply
        }

    # --- Fast-Path 3: Instant Fast-Math Engine (Categories A-E, G, J, L, M) (<1ms) ---
    is_pure, _, _ = try_evaluate_fast_math(question)
    if is_pure:
        print("  [Router: FAST-PATH DETERMINISTIC MATH] -> 'math_calculation'")
        return {
            "routing_decision": "math_calculation",
            "current_question": question,
            "resolved_query": question,
            "active_entities": active_entities,
            "conversation_topic": conversation_topic,
            "depth": "quick"
        }

    # --- Fast-Path 4: Instant Live Market Tickers (<1ms) ---
    # Detect known tickers and track them as active entities deterministically
    known_tickers = {
        "reliance": ("Reliance Industries", "RELIANCE.NS"),
        "tcs": ("Tata Consultancy Services", "TCS.NS"),
        "hdfc": ("HDFC Bank", "HDFCBANK.NS"),
        "infosys": ("Infosys", "INFY.NS"),
        "nifty": ("NIFTY 50", "^NSEI"),
        "sensex": ("BSE SENSEX", "^BSESN"),
        "itc": ("ITC Limited", "ITC.NS"),
    }
    for kw, (cname, ticker) in known_tickers.items():
        if kw in lower and ("price" in lower or "stock" in lower or "quote" in lower or "share" in lower or "ticker" in lower or lower.strip() in [kw, f"{kw} share", f"{kw} stock"]):
            print(f"  [Router: FAST-PATH LIVE MARKET for {cname}] -> 'live_market_data'")
            updated_entities = dict(active_entities or {})
            updated_entities["company"] = cname
            updated_entities["ticker"] = ticker
            topic = f"{cname} Market Data"
            if conv_id:
                save_conversation_continuity(conv_id, updated_entities, topic, user_id=user_id)
            return {
                "routing_decision": "live_market_data",
                "current_question": question,
                "resolved_query": question,
                "active_entities": updated_entities,
                "conversation_topic": topic,
                "depth": depth
            }

    # --- Fast-Path 4a: Statutory Tax / Budget / Regulatory Corpus Knowledge (<1ms) ---
    _CORPUS_KEYWORDS = [
        "80c", "80d", "section 80", "budget 2024", "ltcg", "stcg", 
        "capital gains tax", "tax exemption", "new tax regime", "old tax regime", 
        "income tax slab", "regulatory bulletin", "regulatory directives", "directives for 2026",
        "monthly financial and regulatory"
    ]
    if any(k in lower for k in _CORPUS_KEYWORDS) and not any(r in lower for r in ["calculate", "compute", "my tax", "my salary"]):
        print("  [Router: FAST-PATH STATUTORY TAX/CORPUS] -> 'hybrid_search'")
        return {
            "routing_decision": "hybrid_search",
            "current_question": question,
            "resolved_query": question,
            "active_entities": active_entities,
            "conversation_topic": conversation_topic or "Tax & Regulatory",
            "depth": depth
        }

    # --- Fast-Path 4b: Current Events / Live News (recency signal + finance context) (<1ms) ---
    _RECENCY = {"today", "tonight", "this week", "this month", "latest", "recent",
                "new rules", "what happened", "current", "breaking", "just announced",
                "update", "news"}
    _NEWS_FINANCE = {"rbi", "sebi", "repo", "inflation", "market",
                     "nifty", "sensex", "economy", "finance", "policy", "regulation",
                     "stock", "bank", "interest", "rate", "rupee", "crude", "ipo"}
    has_recency  = any(r in lower for r in _RECENCY)
    has_fin_ctx  = any(f in lower for f in _NEWS_FINANCE)
    if has_recency and has_fin_ctx:
        print("  [Router: FAST-PATH CURRENT EVENTS] -> 'current_events'")
        return {
            "routing_decision": "current_events",
            "current_question": question,
            "resolved_query": question,
            "active_entities": active_entities,
            "conversation_topic": conversation_topic,
            "depth": depth
        }

    # --- Fast-Path 4c: Pronoun Resolution to Active Market Ticker (<1ms) ---
    if any(p in lower for p in ["its price", "its current price", "its stock", "its quote", "its stock price", "what is its price"]):
        active_co = (active_entities or {}).get("company")
        active_tk = (active_entities or {}).get("ticker")
        if active_co or active_tk:
            resolved_q = f"What is the current stock price of {active_co or active_tk}?"
            print(f"  [Router: FAST-PATH PRONOUN RESOLUTION for {active_co}] -> 'live_market_data'")
            return {
                "routing_decision": "live_market_data",
                "current_question": resolved_q,
                "resolved_query": resolved_q,
                "active_entities": active_entities,
                "conversation_topic": conversation_topic or f"{active_co} Market Data",
                "depth": depth
            }

    # --- Fast-Path 5: Instant Arithmetic Keywords with Digits (<1ms) ---
    has_digits = any(char.isdigit() for char in lower)
    has_math_syntax = bool(re.search(r'\d+\s*[\+\*]\s*\d+', lower) or re.search(r'\d+\s+[-/]\s+\d+', lower))
    has_math_words = has_digits and any(op in lower for op in [" add ", " subtract ", " multiply ", " plus ", " minus ", " divided by "])
    is_not_date_or_filing = not bool(re.search(r'\b\d{4}-\d{2,4}\b', lower) or "10-k" in lower or "10-q" in lower or "long-term" in lower)
    if (has_math_syntax or has_math_words) and is_not_date_or_filing:
        print("  [Router: FAST-PATH ARITHMETIC KEYWORDS] -> 'math_calculation'")
        return {
            "routing_decision": "math_calculation",
            "current_question": question,
            "resolved_query": question,
            "active_entities": active_entities,
            "conversation_topic": conversation_topic,
            "depth": depth
        }

    # --- Fast-Path 5a: SIP & Financial Compounding Formulas (<1ms) ---
    if ("sip" in lower or ("monthly" in lower and "invest" in lower)) and any(char.isdigit() for char in lower):
        print("  [Router: FAST-PATH SIP CALCULATION] -> 'calculation'")
        return {
            "routing_decision": "calculation",
            "current_question": question,
            "resolved_query": question,
            "active_entities": active_entities,
            "conversation_topic": conversation_topic or "SIP Compounding",
            "depth": "quick"
        }

    # --- Fast-Path 5b: Personal Surplus / Savings from Memory (<1ms) ---
    if any(w in lower for w in ["surplus", "monthly surplus", "my surplus", "disposable surplus", "how much can i save", "monthly savings"]):
        print("  [Router: FAST-PATH PERSONAL SURPLUS] -> 'calculation'")
        return {
            "routing_decision": "calculation",
            "current_question": question,
            "resolved_query": question,
            "active_entities": active_entities,
            "conversation_topic": conversation_topic or "Budget Surplus",
            "depth": "quick"
        }

    # --- Check 10-Minute Router TTL Cache for exact match repeated queries (only if self-contained) ---
    cache_key = f"{lower}__doc_{bool(document_id)}__ent_{bool(active_entities)}"
    now = time.time()
    if cache_key in _ROUTER_CACHE and not any(pronoun in lower for pronoun in ["its", "this", "they", "them", "that", "these"]):
        cached_decision, cached_depth, expiry = _ROUTER_CACHE[cache_key]
        if now < expiry:
            print(f"  [Router: 10-MIN TTL CACHE HIT] -> '{cached_decision}'")
            return {
                "routing_decision": cached_decision,
                "current_question": question,
                "resolved_query": question,
                "active_entities": active_entities,
                "conversation_topic": conversation_topic,
                "depth": cached_depth
            }

    try:
        # Build arguments for router chain with guaranteed prompt variables
        invoke_args = {
            "question": question,
            "memory_context": memory_context or "None (First interaction)",
            "active_entities": str(active_entities or "None"),
            "conversation_topic": str(conversation_topic or "None"),
        }
        route = router_chain.invoke(invoke_args)
        decision = route.decision
        is_topic_change = bool(getattr(route, "is_topic_change", False))
        resolved_q = getattr(route, "resolved_query", None) or question

        if is_topic_change:
            # ADVERSARIAL TOPIC SHIFT: Completely reset previous entities to prevent context poisoning
            print("  [Router] Detected topic shift — resetting active entities!")
            updated_entities = {}
            if getattr(route, "extracted_entities", None):
                for k, v in route.extracted_entities.items():
                    if v:
                        updated_entities[k] = v
            updated_topic = getattr(route, "conversation_topic", "") or "General Finance"
        else:
            updated_entities = dict(active_entities or {})
            if getattr(route, "extracted_entities", None):
                for k, v in route.extracted_entities.items():
                    if v:
                        updated_entities[k] = v
            updated_topic = getattr(route, "conversation_topic", "") or conversation_topic or ""

    except Exception as e:
        print(f"Router fallback due to: {e}")
        is_calculation_query = any(term in lower for term in ["calculate", "compute", "how much is", "what is the return on"])
        
        # Check topic shift heuristic in fallback
        is_unrelated_concept = any(term in lower for term in ["compound interest", "wacc", "npv", "cagr", "sip", "emi", "section 80c", "tax slab"])
        if is_unrelated_concept and active_entities.get("company"):
            print("  [Router Fallback] Heuristic topic shift detected — resetting active entities.")
            updated_entities = {}
            updated_topic = "Financial Concepts"
            resolved_q = question
        elif active_entities.get("company") and any(pronoun in lower for pronoun in ["its ", "it's ", "their ", "this company"]):
            company = active_entities["company"]
            resolved_q = question.replace("its ", f"{company}'s ").replace("it's ", f"{company}'s ").replace("this company", company)
            updated_entities = dict(active_entities)
            updated_topic = conversation_topic
        else:
            resolved_q = question
            updated_entities = dict(active_entities or {})
            updated_topic = conversation_topic or ""

        if any(term in lower for term in ["reliance", "tcs", "hdfc", "nifty", "sensex", "stock", "price"]):
            decision = "live_market_data"
        elif has_digits and any(term in lower for term in ["add", "subtract", "multiply", "divide", "plus", "minus"]):
            decision = "math_calculation"
        elif has_digits and is_calculation_query and any(term in lower for term in ["wacc", "npv", "cagr", "dcf", "yoy", "growth", "margin", "interest", "sip", "emi", "irr"]):
            decision = "calculation"
        elif any(term in lower for term in ["what is", "define", "explain", "how does", "formula for", "definition", "rule", "rules", "tax", "budget", "finance", "regulation", "guideline", "rbi", "sebi"]):
            decision = "hybrid_search"
        elif any(term in lower for term in ["wacc", "npv", "cagr", "dcf", "yoy", "growth", "margin"]):
            decision = "calculation"
        else:
            decision = "direct_answer"

    # Persist updated continuity state scoped to this conversation & user
    if conv_id:
        save_conversation_continuity(conv_id, updated_entities, updated_topic, user_id=user_id)

    # -------------------------------------------------------------------------
    # DOCUMENT MODE OVERRIDE
    # When a personal document is attached, every question about the document
    # must pass through the retriever (exclusive personal-doc path).
    # Only queries with explicit digits AND math keywords are sent to math solver.
    # -------------------------------------------------------------------------
    if document_id:
        lower_q = resolved_q.lower()
        has_digits = any(char.isdigit() for char in lower_q)
        is_explicit_math = has_digits and any(term in lower_q for term in ["add", "subtract", "multiply", "divide", "plus", "minus", "sum", "total", "cagr", "sip", "wacc", "npv", "dcf", "emi"])
        if not is_explicit_math:
            print(f"  [Router: DOCUMENT MODE] overriding '{decision}' → 'hybrid_search'")
            decision = "hybrid_search"

    # Save into 10-min router cache if self-contained
    if not any(pronoun in lower for pronoun in ["its", "this", "they", "them", "that", "these"]):
        _ROUTER_CACHE[cache_key] = (decision, depth, now + _ROUTER_CACHE_TTL)

    print(f"Decision: {decision}, Depth: {depth}, Topic: {updated_topic}, Entities: {updated_entities}")
    return {
        "routing_decision": decision,
        "current_question": resolved_q,
        "resolved_query": resolved_q,
        "active_entities": updated_entities,
        "conversation_topic": updated_topic,
        "depth": depth
    }



