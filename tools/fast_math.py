"""
Unified Fast-Math Engine for FinAdvisor.
Deterministically processes math queries across Categories A, B, C, D, E, G, J, L, and M
using safe AST evaluation, regex pattern matchers, and statistics/datetime modules.
Zero LLM calls, zero arbitrary eval().
"""
import ast
import operator
import re
import math
import statistics
from datetime import datetime, date, timedelta
from typing import Tuple, Optional, List, Dict, Any, Union

# -----------------------------------------------------------------------------
# CATEGORY A: AST OPERATORS & RECURSIVE EVALUATOR
# -----------------------------------------------------------------------------

_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

MAX_NUMBER_LIMIT = 10**18  # Sane upper bound against CPU explosion


def _safe_eval_ast(node: ast.AST) -> float:
    """Recursively evaluates restricted AST nodes safely."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            val = float(node.value)
            if abs(val) > MAX_NUMBER_LIMIT:
                raise OverflowError("Number exceeds maximum computational limit (10^18).")
            return val
        raise ValueError(f"Unsupported constant type: {type(node.value)}")

    if hasattr(ast, "Num") and isinstance(node, getattr(ast, "Num")):
        val = float(node.n)
        if abs(val) > MAX_NUMBER_LIMIT:
            raise OverflowError("Number exceeds maximum computational limit (10^18).")
        return val

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPS:
            raise ValueError(f"Unsupported binary operator: {op_type}")
        left_val = _safe_eval_ast(node.left)
        right_val = _safe_eval_ast(node.right)

        if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right_val == 0:
            raise ZeroDivisionError("Division by zero is undefined.")

        if op_type == ast.Pow:
            if right_val < 0 and left_val == 0:
                raise ZeroDivisionError("Division by zero in power calculation.")
            if abs(right_val) > 1000 or (abs(left_val) > 1000 and right_val > 50):
                raise OverflowError("Number exceeds maximum computational limit (10^18).")
            # Check for fractional power of negative number (complex result)
            if left_val < 0 and not right_val.is_integer():
                raise ValueError("Result is not a real number.")

        res = _ALLOWED_OPS[op_type](left_val, right_val)
        if isinstance(res, (int, float)) and abs(res) > MAX_NUMBER_LIMIT:
            raise OverflowError("Number exceeds maximum computational limit (10^18).")
        return float(res)

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPS:
            raise ValueError(f"Unsupported unary operator: {op_type}")
        operand_val = _safe_eval_ast(node.operand)
        res = _ALLOWED_OPS[op_type](operand_val)
        return float(res)

    if isinstance(node, ast.Expression):
        return _safe_eval_ast(node.body)

    raise ValueError(f"Unsupported AST node: {ast.dump(node)}")


# -----------------------------------------------------------------------------
# CATEGORY C & L: NUMBER WORDS & INDIAN NUMBERING NORMALIZATION
# -----------------------------------------------------------------------------

_WORD_TO_NUM = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
    "hundred": 100, "thousand": 1000, "k": 1000,
    "lakh": 100000, "lakhs": 100000, "lac": 100000, "lacs": 100000,
    "crore": 10000000, "crores": 10000000, "cr": 10000000,
    "million": 1000000, "m": 1000000, "billion": 1000000000, "b": 1000000000,
}

_WORD_OPERATORS = [
    (r"\bmultiplied\s+by\b", "*"),
    (r"\bmultiply\b", "*"),
    (r"\btimes\b", "*"),
    (r"\binto\b", "*"),
    (r"\bdivided\s+by\b", "/"),
    (r"\bdivide\b", "/"),
    (r"\bover\b", "/"),
    (r"\bplus\b", "+"),
    (r"\badd\b", "+"),
    (r"\band\b", "+"),
    (r"\bminus\b", "-"),
    (r"\bsubtract\b", "-"),
    (r"\bpercent\b", "%"),
    (r"\bpercentage\b", "%"),
]


def format_indian_number(val: float, currency_symbol: str = "") -> str:
    """
    Formats a numeric value with Indian digit grouping (e.g. 7,50,000 or 1,25,00,000)
    and optional currency prefix.
    """
    is_negative = val < 0
    val = abs(val)

    if val.is_integer():
        int_part = str(int(val))
        dec_part = ""
    else:
        # Show up to 6 significant decimals without trailing zeroes
        dec_formatted = f"{val:.6f}".rstrip("0").rstrip(".")
        parts = dec_formatted.split(".")
        int_part = parts[0]
        dec_part = "." + parts[1] if len(parts) > 1 else ""

    # Indian comma grouping algorithm:
    # Rightmost 3 digits, then groups of 2 digits
    if len(int_part) <= 3:
        grouped = int_part
    else:
        last3 = int_part[-3:]
        remaining = int_part[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        grouped = ",".join(groups) + "," + last3

    sign = "-" if is_negative else ""
    curr = f"{currency_symbol} " if currency_symbol and currency_symbol.isalpha() else (currency_symbol or "")
    return f"{sign}{curr}{grouped}{dec_part}".strip()


def format_western_number(val: float, currency_symbol: str = "") -> str:
    """Formats a numeric value with Western comma grouping (e.g. 1,000,000.00)."""
    is_negative = val < 0
    val = abs(val)

    if val.is_integer():
        int_part = f"{int(val):,}"
        dec_part = ""
    else:
        dec_formatted = f"{val:.6f}".rstrip("0").rstrip(".")
        parts = dec_formatted.split(".")
        int_part = f"{int(parts[0]):,}"
        dec_part = "." + parts[1] if len(parts) > 1 else ""

    sign = "-" if is_negative else ""
    curr = f"{currency_symbol} " if currency_symbol and currency_symbol.isalpha() else (currency_symbol or "")
    return f"{sign}{curr}{int_part}{dec_part}".strip()


def detect_currency_and_style(raw_text: str) -> Tuple[str, str]:
    """
    Detects currency symbol and numbering style (Indian vs Western).
    Returns (currency_symbol, 'indian' | 'western').
    """
    text_lower = raw_text.lower()
    symbol = ""
    style = "western"

    if "₹" in raw_text:
        symbol = "₹"
        style = "indian"
    elif "rs." in text_lower or "rs " in text_lower or "rs" in text_lower.split():
        symbol = "₹"
        style = "indian"
    elif "inr" in text_lower:
        symbol = "₹"
        style = "indian"
    elif "$" in raw_text or "usd" in text_lower:
        symbol = "$"
        style = "western"
    elif "€" in raw_text or "eur" in text_lower:
        symbol = "€"
        style = "western"
    elif "£" in raw_text or "gbp" in text_lower:
        symbol = "£"
        style = "western"

    # If lakh/crore mentioned, default to Indian format
    if any(term in text_lower for term in ["lakh", "lakhs", "lac", "lacs", "crore", "crores", "cr"]):
        style = "indian"
        if not symbol:
            symbol = "₹"

    # Check comma style in numbers (e.g. 5,00,000 vs 500,000)
    if re.search(r'\b\d{1,2},\d{2},\d{3}\b', raw_text):
        style = "indian"

    return symbol, style


def format_final_result(val: float, currency_symbol: str = "", style: str = "indian") -> str:
    """Formats final numeric response in bold according to detected currency and locale."""
    if style == "indian" or currency_symbol == "₹":
        num_str = format_indian_number(val, currency_symbol)
    else:
        num_str = format_western_number(val, currency_symbol)
    return f"**The calculated result is {num_str}.**"


def normalize_lakh_crore_terms(text: str) -> str:
    """Converts '5 lakh' -> '500000', '2.5 crore' -> '25000000', etc."""
    def _repl_lakh_crore(m):
        num = float(m.group(1))
        unit = m.group(2).lower()
        multiplier = 100000 if unit in ("lakh", "lakhs", "lac", "lacs") else (10000000 if unit in ("crore", "crores", "cr") else (1000 if unit in ("k", "thousand") else 1000000))
        val = num * multiplier
        return str(int(val)) if val.is_integer() else str(val)

    pattern = re.compile(r'(\d+(?:\.\d+)?)\s*(lakhs?|lacs?|crores?|cr|thousand|k|million|billion)\b', re.IGNORECASE)
    return pattern.sub(_repl_lakh_crore, text)


def normalize_words_to_math_expression(text: str) -> str:
    """
    Converts natural language math phrases into clean arithmetic expressions.
    E.g. 'what is two plus two' -> '2 + 2', 'multiply five by six' -> '5 * 6'.
    """
    cleaned = text.lower().strip()

    # Strip conversational filler prefixes
    cleaned = re.sub(r'^(what\s+is|what\'s|whats|calculate|compute|solve|how\s+much\s+is|find|evaluate|tell\s+me)\s+', '', cleaned)
    cleaned = re.sub(r'[^\w\s\.\+\-\*\/\%\^\(\)\,\:\₹\$\€\£]', ' ', cleaned)

    # Normalize lakh/crore
    cleaned = normalize_lakh_crore_terms(cleaned)

    # First pass: replace word numbers with digits
    tokens = cleaned.split()
    normalized_tokens = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in _WORD_TO_NUM:
            val = _WORD_TO_NUM[t]
            # Check for compounds like 'twenty five'
            if i + 1 < len(tokens) and tokens[i + 1] in _WORD_TO_NUM:
                next_val = _WORD_TO_NUM[tokens[i + 1]]
                if val in (20, 30, 40, 50, 60, 70, 80, 90) and next_val < 10:
                    val += next_val
                    i += 1
                elif next_val in (100, 1000, 100000, 10000000):
                    val *= next_val
                    i += 1
            normalized_tokens.append(str(val))
        else:
            normalized_tokens.append(t)
        i += 1

    result = " ".join(normalized_tokens)

    # Handle verbal binary constructs
    result = re.sub(r'\bmultiply\s+(\d+(?:\.\d+)?)\s+by\s+(\d+(?:\.\d+)?)\b', r'\1 * \2', result)
    result = re.sub(r'\bdivide\s+(\d+(?:\.\d+)?)\s+by\s+(\d+(?:\.\d+)?)\b', r'\1 / \2', result)
    result = re.sub(r'\badd\s+(\d+(?:\.\d+)?)\s+(?:to|and)\s+(\d+(?:\.\d+)?)\b', r'\1 + \2', result)
    result = re.sub(r'\bsubtract\s+(\d+(?:\.\d+)?)\s+from\s+(\d+(?:\.\d+)?)\b', r'\2 - \1', result)

    # Replace remaining word operators
    for pat, rep in _WORD_OPERATORS:
        result = re.sub(pat, f" {rep} ", result)

    # Strip currency and commas from numbers
    result = re.sub(r'[\₹\$\€\£]', '', result)
    result = re.sub(r'(?<=\d),(?=\d)', '', result)
    return result.strip()



# -----------------------------------------------------------------------------
# CATEGORY B: PERCENTAGES, DISCOUNTS, RATIOS, FRACTIONS
# -----------------------------------------------------------------------------

def evaluate_percentage_and_ratio_patterns(raw_text: str, currency_symbol: str, style: str) -> Tuple[bool, Optional[str], Optional[float]]:
    """Evaluates percentage of, discounts, markups, fractions, and ratio splits."""
    text = raw_text.lower().strip()
    text_clean = normalize_lakh_crore_terms(text)
    # Strip commas and currency symbols inside numeric patterns
    text_clean = re.sub(r'[\₹\$\€\£]', '', text_clean)
    text_clean = re.sub(r'(?<=\d),(?=\d)', '', text_clean)

    # 1. "X% discount on Y" / "X% off on Y" / "X% off Y"
    discount_match = re.search(r'(\d+(?:\.\d+)?)\s*%\s*(?:discount\s+on|off\s+on|off)\s+(\d+(?:\.\d+)?)', text_clean)
    if discount_match:
        pct = float(discount_match.group(1))
        base = float(discount_match.group(2))
        discount_amount = (pct / 100.0) * base
        final_val = base - discount_amount
        base_f = format_indian_number(base, currency_symbol) if style == "indian" else format_western_number(base, currency_symbol)
        disc_f = format_indian_number(discount_amount, currency_symbol) if style == "indian" else format_western_number(discount_amount, currency_symbol)
        final_f = format_indian_number(final_val, currency_symbol) if style == "indian" else format_western_number(final_val, currency_symbol)
        ans = (
            f"**The discounted amount is {final_f}.**\n\n"
            f"* **Original Amount**: {base_f}\n"
            f"* **Discount ({pct}% off)**: -{disc_f}\n"
            f"* **Final Payable**: **{final_f}**"
        )
        return True, ans, final_val

    # 2. "X% increase on Y" / "X% hike on Y" / "X% markup on Y" / "X% tax on Y"
    hike_match = re.search(r'(\d+(?:\.\d+)?)\s*%\s*(?:increase\s+on|hike\s+on|markup\s+on|tax\s+on)\s+(\d+(?:\.\d+)?)', text_clean)
    if hike_match:
        pct = float(hike_match.group(1))
        base = float(hike_match.group(2))
        hike_amount = (pct / 100.0) * base
        final_val = base + hike_amount
        final_f = format_indian_number(final_val, currency_symbol) if style == "indian" else format_western_number(final_val, currency_symbol)
        return True, f"**The calculated total is {final_f}** (Base: {base:,.2f} + {pct}%: {hike_amount:,.2f}).", final_val

    # 3. "X% of Y" / "X percent of Y"
    pct_of_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:%|\s*percent)\s+of\s+(\d+(?:\.\d+)?)', text_clean)
    if pct_of_match:
        pct = float(pct_of_match.group(1))
        base = float(pct_of_match.group(2))
        res = (pct / 100.0) * base
        return True, format_final_result(res, currency_symbol, style), res

    # 4. "a/b of Y" (Fractions)
    frac_match = re.search(r'(\d+(?:\.\d+)?)\s*\/\s*(\d+(?:\.\d+)?)\s+of\s+(\d+(?:\.\d+)?)', text_clean)
    if frac_match:
        a = float(frac_match.group(1))
        b = float(frac_match.group(2))
        base = float(frac_match.group(3))
        if b == 0:
            return True, "**Division by zero is undefined.**", None
        res = (a / b) * base
        return True, format_final_result(res, currency_symbol, style), res

    # 5. "split Y in [a:b | a to b | a and b] ratio"
    ratio_match = re.search(r'split\s+(\d+(?:\.\d+)?)\s+(?:in|into|in\s+a)\s+(\d+(?:\.\d+)?)\s*(?::|to|\/)\s*(\d+(?:\.\d+)?)\s*(?:ratio)?', text_clean)
    if ratio_match:
        total = float(ratio_match.group(1))
        a = float(ratio_match.group(2))
        b = float(ratio_match.group(3))
        if (a + b) == 0:
            return True, "**Ratio sum cannot be zero.**", None
        share_a = (total * a) / (a + b)
        share_b = (total * b) / (a + b)
        share_a_f = format_indian_number(share_a, currency_symbol) if style == "indian" else format_western_number(share_a, currency_symbol)
        share_b_f = format_indian_number(share_b, currency_symbol) if style == "indian" else format_western_number(share_b, currency_symbol)
        ans = (
            f"**The ratio split ({a}:{b}) of {format_indian_number(total, currency_symbol)} is:**\n\n"
            f"* **Part 1 ({a}/{a+b:g})**: **{share_a_f}**\n"
            f"* **Part 2 ({b}/{a+b:g})**: **{share_b_f}**"
        )
        return True, ans, share_a

    return False, None, None


# -----------------------------------------------------------------------------
# CATEGORY E: STATISTICAL CALCULATIONS (AVERAGE, MEDIAN, STD DEV, MIN, MAX)
# -----------------------------------------------------------------------------

_STATS_KEYWORDS = {
    "average": statistics.mean,
    "mean": statistics.mean,
    "median": statistics.median,
    "std dev": statistics.stdev,
    "standard deviation": statistics.stdev,
    "variance": statistics.variance,
    "min": min,
    "minimum": min,
    "max": max,
    "maximum": max,
}


def evaluate_statistics(raw_text: str, currency_symbol: str, style: str) -> Tuple[bool, Optional[str], Optional[float]]:
    """Evaluates statistical functions across a list of extracted numbers."""
    text_lower = raw_text.lower().strip()

    # Identify statistical operation
    op_name = None
    stat_func = None
    for kw, func in _STATS_KEYWORDS.items():
        if re.search(rf'\b{re.escape(kw)}\b', text_lower):
            op_name = kw
            stat_func = func
            break

    if not stat_func:
        return False, None, None

    # Extract all numbers/percentages in order
    # Handles: '12%, 8%, 15%, -3%' or '500, 700, 300, 900'
    text_norm = normalize_lakh_crore_terms(text_lower)
    text_norm = re.sub(r'[\₹\$\€\£]', '', text_norm)
    
    # Extract numbers with signs and optional decimals
    num_matches = re.findall(r'[-+]?\d*\.?\d+(?:%)?', text_norm)
    if not num_matches or len(num_matches) < 2:
        return False, None, None

    numbers = []
    is_percentage_list = any('%' in m for m in num_matches)
    for m in num_matches:
        cleaned_m = m.replace('%', '').strip()
        try:
            val = float(cleaned_m)
            numbers.append(val)
        except ValueError:
            continue

    if len(numbers) < 2:
        return False, None, None

    try:
        if op_name in ("std dev", "standard deviation", "variance") and len(numbers) < 2:
            return True, "**Standard deviation requires at least 2 data points.**", None

        result = stat_func(numbers)
        result_float = float(result)

        unit = "%" if is_percentage_list else ""
        if is_percentage_list:
            formatted_res = f"{result_float:,.2f}%"
        elif style == "indian" or currency_symbol == "₹":
            formatted_res = format_indian_number(result_float, currency_symbol)
        else:
            formatted_res = format_western_number(result_float, currency_symbol)

        num_list_str = ", ".join([f"{n:g}{unit}" for n in numbers])
        op_title = op_name.title()
        ans = (
            f"**The {op_title} is {formatted_res}.**\n\n"
            f"* **Data Points ({len(numbers)})**: `[{num_list_str}]`\n"
            f"* **Computed {op_title}**: **{formatted_res}**"
        )
        return True, ans, result_float
    except Exception as e:
        return False, None, None


# -----------------------------------------------------------------------------
# CATEGORY G: DATE & TENURE-BASED CALCULATIONS
# -----------------------------------------------------------------------------

_MONTHS = {
    "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
    "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6,
    "july": 7, "jul": 7, "august": 8, "aug": 8, "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10, "november": 11, "nov": 11, "december": 12, "dec": 12
}


def evaluate_date_and_tenure_math(raw_text: str) -> Tuple[bool, Optional[str], Optional[float]]:
    """Evaluates date differences, maturity years, and age projections."""
    text_lower = raw_text.lower().strip()
    today = date.today()

    # 1. "how old will I be in <TargetYear> if I'm <CurrentAge> now"
    age_match = re.search(r'(?:how\s+old\s+will\s+i\s+be\s+in\s+(\d{4})|age\s+in\s+(\d{4})).*?(?:i\'?m|am|age)\s+(\d{1,3})', text_lower)
    if age_match:
        target_year = int(age_match.group(1) or age_match.group(2))
        current_age = int(age_match.group(3))
        diff = target_year - today.year
        future_age = current_age + diff
        ans = (
            f"**In {target_year}, you will be {future_age} years old.**\n\n"
            f"* **Current Age**: {current_age} (as of {today.year})\n"
            f"* **Years Elapsed**: +{diff} years\n"
            f"* **Projected Age**: **{future_age} years old**"
        )
        return True, ans, float(future_age)

    # 2. "what year does a <N>-year FD mature" / "maturity year of <N> year bond"
    fd_match = re.search(r'(\d+(?:\.\d+)?)\s*[- ]*(?:year|yr)s?\s*(?:fd|fixed\s+deposit|bond|investment|policy|loan|tenure|plan)', text_lower)
    if fd_match and any(w in text_lower for w in ["mature", "maturity", "expire", "end", "complete", "finish"]):
        tenure_years = float(fd_match.group(1))
        maturity_year = int(today.year + tenure_years)
        ans = (
            f"**A {tenure_years:g}-year investment started today ({today.strftime('%d %B %Y')}) will mature in {maturity_year}.**"
        )
        return True, ans, float(maturity_year)

    # 3. "how many days until <Day> <Month> <Year>" (e.g. 15 March 2027)
    days_until_match = re.search(r'(?:how\s+many\s+days\s+until|days\s+(?:left\s+)?to)\s+(\d{1,2})\s+([a-z]+)\s+(\d{4})', text_lower)
    if days_until_match:
        day_num = int(days_until_match.group(1))
        month_name = days_until_match.group(2).lower()
        year_num = int(days_until_match.group(3))
        if month_name in _MONTHS:
            try:
                target_date = date(year_num, _MONTHS[month_name], day_num)
                delta_days = (target_date - today).days
                if delta_days >= 0:
                    ans = f"**There are {delta_days:,} days remaining until {target_date.strftime('%d %B %Y')}.**"
                else:
                    ans = f"**{target_date.strftime('%d %B %Y')} was {abs(delta_days):,} days ago.**"
                return True, ans, float(delta_days)
            except ValueError:
                return False, None, None

    return False, None, None


# -----------------------------------------------------------------------------
# CATEGORY J: SEQUENTIAL MULTI-STEP CALCULATIONS
# -----------------------------------------------------------------------------

def evaluate_sequential_math(raw_text: str, currency_symbol: str, style: str) -> Tuple[bool, Optional[str], Optional[float]]:
    """
    Evaluates multi-step math in one message.
    E.g. 'calculate 12% of 50000, then add 8% of that result'
    """
    text = raw_text.lower().strip()
    if "then" not in text and "and then" not in text:
        return False, None, None

    steps = re.split(r'\b(?:then\s+also|then|and\s+then)\b', text)
    if len(steps) != 2:
        return False, None, None

    step1_str = steps[0].strip()
    step2_str = steps[1].strip()

    # Evaluate step 1
    is_step1, ans1, val1 = try_evaluate_fast_math(step1_str)
    if not is_step1 or val1 is None:
        return False, None, None

    # Step 2: substitute backreferences ('that', 'that result', 'it', 'the result') with val1
    step2_substituted = re.sub(r'\b(that\s+result|that\s+number|that|it|the\s+result)\b', str(val1), step2_str)

    # Check for "add X% of that" or "add X"
    pct_add_match = re.search(r'(?:add|plus|\+)\s*(\d+(?:\.\d+)?)\s*%\s*(?:of\s+)?(\d+(?:\.\d+)?)?', step2_substituted)
    if pct_add_match:
        pct = float(pct_add_match.group(1))
        sub_base = float(pct_add_match.group(2)) if pct_add_match.group(2) else val1
        add_amount = (pct / 100.0) * sub_base
        final_val = val1 + add_amount
        ans = (
            f"**The final calculated result is {format_indian_number(final_val, currency_symbol) if style == 'indian' else format_western_number(final_val, currency_symbol)}.**\n\n"
            f"* **Step 1 Result**: {format_indian_number(val1, currency_symbol)}\n"
            f"* **Step 2 ({pct}% of {sub_base:g})**: +{format_indian_number(add_amount, currency_symbol)}\n"
            f"* **Total**: **{format_indian_number(final_val, currency_symbol)}**"
        )
        return True, ans, final_val

    # Generic evaluation for substituted Step 2
    is_step2, ans2, val2 = try_evaluate_fast_math(step2_substituted)
    if is_step2 and val2 is not None:
        ans = (
            f"**The sequential calculation result is {format_indian_number(val2, currency_symbol) if style == 'indian' else format_western_number(val2, currency_symbol)}.**\n\n"
            f"* **Step 1**: {val1:g}\n"
            f"* **Final Step**: **{val2:g}**"
        )
        return True, ans, val2

    return False, None, None


# -----------------------------------------------------------------------------
# UNIFIED ENTRYPOINT: try_evaluate_fast_math
# -----------------------------------------------------------------------------

def try_evaluate_fast_math(query: str) -> Tuple[bool, Optional[str], Optional[float]]:
    """
    Unified deterministic math evaluator covering Categories A through M.
    Returns:
        (is_math, formatted_answer, numeric_result)
    
    If query is not deterministic fast math or malformed, returns (False, None, None).
    """
    if not query:
        return False, None, None

    raw_query = query.strip()
    if not raw_query:
        return False, None, None

    currency_symbol, style = detect_currency_and_style(raw_query)

    # 1. CATEGORY G: Date / Tenure math
    is_date, date_ans, date_val = evaluate_date_and_tenure_math(raw_query)
    if is_date:
        return True, date_ans, date_val

    # 2. CATEGORY J: Sequential multi-step math
    is_seq, seq_ans, seq_val = evaluate_sequential_math(raw_query, currency_symbol, style)
    if is_seq:
        return True, seq_ans, seq_val

    # 3. CATEGORY E: Statistical calculations (average, median, std dev, sum, min, max)
    is_stat, stat_ans, stat_val = evaluate_statistics(raw_query, currency_symbol, style)
    if is_stat:
        return True, stat_ans, stat_val

    # 4. CATEGORY B: Percentages, discounts, markups, fractions, ratio splits
    is_pct, pct_ans, pct_val = evaluate_percentage_and_ratio_patterns(raw_query, currency_symbol, style)
    if is_pct:
        return True, pct_ans, pct_val

    # 5. CATEGORY C & D: Number words, operators & currency normalization
    normalized_expr = normalize_words_to_math_expression(raw_query)

    # 6. CATEGORY A & M: Pure arithmetic AST evaluation
    # Expression must contain only safe characters
    cleaned_expr = normalized_expr.replace("^", "**").replace(" ", "")
    
    # Must contain at least one digit
    if not any(c.isdigit() for c in cleaned_expr):
        return False, None, None

    # Check for valid arithmetic grammar (only digits, operators, parens)
    if not re.match(r'^[0-9\.\+\-\*\/\%\(\)]+$', cleaned_expr):
        return False, None, None

    # Must contain at least one operator to be an actual arithmetic expression
    if not any(op in cleaned_expr for op in ["+", "-", "*", "/", "%"]):
        return False, None, None

    try:
        parsed_tree = ast.parse(cleaned_expr, mode="eval")
        result = _safe_eval_ast(parsed_tree)
        formatted_ans = format_final_result(result, currency_symbol, style)
        return True, formatted_ans, result
    except ZeroDivisionError as zde:
        return True, f"**Division by zero is undefined.** ({str(zde)})", None
    except OverflowError as oe:
        return True, f"**{str(oe)}**", None
    except ValueError as ve:
        if "not a real number" in str(ve).lower():
            return True, "**Result is not a real number.**", None
        return False, None, None
    except (SyntaxError, Exception):
        # Malformed expression, fall through to the graph pipeline gracefully
        return False, None, None
