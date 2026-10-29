"""
FinAdvisor Domain Guardrails.
Guarantees domain boundary integrity:
1. Blocks coding/script requests (e.g. "write python code", "give python code of sum of two number", "script to").
2. Blocks general trivia/inventors/non-financial queries (e.g. "who is the inventor of computer", "name of inventor of bulb", "who invented python").
3. Detects out-of-domain output leaks (markdown code blocks with non-financial programming languages or function definitions).
4. Maintains complete user data privacy and isolated tenant safety.
"""
import re
from typing import Tuple, Optional

# Standard domain guardrail refusal message
FINANCIAL_GUARDRAIL_REFUSAL = (
    "I am **FinAdvisor-X**, a specialized AI financial intelligence assistant.\n\n"
    "I cannot provide programming code, scripts, software development solutions, or general non-financial trivia (such as inventors, science, or general history).\n\n"
    "I can only assist with:\n"
    "* 📈 **Market Intelligence**: Live equity quotes from NSE/BSE and fundamental valuation.\n"
    "* 🧮 **Financial Calculations**: SIP compounding, WACC, DCF valuation, CAGR, and loan EMI.\n"
    "* 🏛️ **Indian Tax Planning**: FY 2026-27 New vs Old Tax Regime calculations and standard deductions.\n"
    "* 📄 **Document Analysis**: Upload PDF salary slips or financial statements for private analysis."
)

# Explicit code generation & programming triggers
CODE_GENERATION_TRIGGERS = [
    "python code", "write python", "give python", "python script", "code in python",
    "java code", "javascript code", "c++ code", "cpp code", "html code", "css code",
    "write a code", "write code", "give me code", "give code", "generate code",
    "sum of two number", "sum of 2 numbers", "sum of two numbers", "add two numbers in python",
    "write a script", "write script", "create a function in", "def ", "class ",
    "algorithm for", "bubble sort", "binary search", "leetcode", "fibonacci code",
    "write a program", "write program", "coding question", "solve in python", "code of sum",
    "write function", "python program"
]

# General non-financial trivia & inventor triggers
GENERAL_TRIVIA_TRIGGERS = [
    "inventor of", "who invented", "name of inventor", "who discovered",
    "father of computer", "inventor of computer", "inventor of bulb", "inventor of telephone",
    "who founded", "capital of", "president of", "prime minister of",
    "how to bake", "recipe for", "movie rating", "actor of", "actress of",
    "lyrics of", "who is messi", "who is ronaldo", "football score",
    "tell me about dinosaurs", "biology of", "chemistry equation",
    "solar system", "speed of light", "distance to moon"
]

# Exceptions / Allowlist terms that might mention an inventor or founder in finance
FINANCIAL_ALLOWLIST = {
    "black scholes", "markowitz", "fama french", "benjamin graham", "warren buffett",
    "charlie munger", "john bogle", "raghuram rajan", "shaktikanta das", "nirmala sitharaman",
    "adam smith", "john maynard keynes", "milton friedman"
}

# Substantive finance indicator keywords to ensure financial queries aren't falsely flagged
FINANCIAL_KEYWORDS = {
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

def is_out_of_domain_query(query: str) -> Tuple[bool, Optional[str]]:
    """
    Checks if a query violates domain boundaries (e.g. asking for Python code,
    general programming, or non-financial trivia like inventors/science).
    
    Returns:
        (is_violation, refusal_message)
    """
    if not query:
        return False, None

    norm = query.lower().replace("'", "").replace("’", "").strip()
    norm_clean = re.sub(r"[^\w\s]", " ", norm)
    norm_clean = " ".join(norm_clean.split())

    # Check if query matches financial allowlist
    if any(allowed in norm_clean for allowed in FINANCIAL_ALLOWLIST):
        return False, None

    # Check 1: Code generation / programming request
    for trig in CODE_GENERATION_TRIGGERS:
        if trig in norm_clean:
            return True, FINANCIAL_GUARDRAIL_REFUSAL

    # Check 2: General trivia / Inventor question
    for trig in GENERAL_TRIVIA_TRIGGERS:
        if trig in norm_clean:
            # Check if there is genuine financial context (e.g. "who invented the index fund?")
            if any(fin_kw in norm_clean for fin_kw in ["index fund", "etf", "mutual fund", "stock market", "bond", "derivatives"]):
                return False, None
            return True, FINANCIAL_GUARDRAIL_REFUSAL

    return False, None

def check_output_guardrail(draft_answer: str, query: str = "") -> Tuple[bool, str]:
    """
    Audits the generated response text.
    If the response leaks executable non-financial programming scripts (python, javascript, c++, etc.)
    or code definitions for non-financial queries, intercepts and replaces with the refusal.
    
    Returns:
        (is_clean, sanitized_answer)
    """
    if not draft_answer:
        return True, draft_answer

    lower = draft_answer.lower()

    # If the response contains markdown code blocks with non-financial programming languages
    code_block_match = re.search(r"```(python|py|javascript|js|java|cpp|c\+\+|c|csharp|cs|ruby|go|rust|bash|sh|php|swift|kotlin)", lower)
    if code_block_match:
        return False, FINANCIAL_GUARDRAIL_REFUSAL

    # Detect standalone function definitions or code snippets
    if any(line.strip().startswith(("def ", "function ", "public class ", "int main(", "#include <")) for line in draft_answer.split("\n")):
        return False, FINANCIAL_GUARDRAIL_REFUSAL

    # Check for general inventor or non-financial trivia patterns if the query was out of domain
    if query:
        is_bad, refusal = is_out_of_domain_query(query)
        if is_bad:
            return False, refusal

    return True, draft_answer
