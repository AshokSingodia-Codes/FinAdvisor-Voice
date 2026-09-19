"""
Deterministic financial math tools. NO LLM involved in extraction —
regex/parsing only, so results are 100% reproducible and testable.
"""
import re
import ast
import operator


# ---------- SAFE EXPRESSION EVALUATOR (for basic +,-,*,/,%) ----------

_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def safe_calculate(expression: str) -> float:
    """Evaluates basic arithmetic without eval(). Raises ValueError on anything unsafe."""
    def _eval(node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Unsupported constant: {node.value}")
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
            return _ALLOWED_OPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
            return _ALLOWED_OPS[type(node.op)](_eval(node.operand))
        if isinstance(node, ast.Tuple):
            return tuple(_eval(elt) for elt in node.elts)
        raise ValueError(f"Unsupported expression element: {ast.dump(node)}")

    try:
        tree = ast.parse(expression, mode="eval")
        return _eval(tree.body)
    except (SyntaxError, ValueError) as e:
        raise ValueError(f"Could not safely evaluate '{expression}': {e}")


# ---------- EXTRACTION (deterministic, no LLM) ----------

_CURRENCY_PATTERN = re.compile(r'(?i)(rs\.?\s?|inr\s?|₹|\$|usd\s?)')
_NUMBER_PATTERN = re.compile(r'-?\d[\d,]*\.?\d*')
_PERCENT_PATTERN = re.compile(r'(-?\d+\.?\d*)\s*%')
_YEARS_PATTERN = re.compile(r'(\d+\.?\d*)\s*(?:years?|yrs?)', re.IGNORECASE)
_DECLINE_KEYWORDS = re.compile(r'(?i)\b(lose|loses|losing|lost|declin\w*|depreciat\w*|drop\w*|fall\w*|shrink\w*|decreas\w*)\b')

def normalize_currency(text: str) -> float | None:
    """
    Extracts a numeric value from any currency format: ₹, Rs., Rs, INR, $, USD,
    Indian (lakh/crore, e.g. 1,25,00,000) or Western comma grouping.
    Returns None if no number found — caller must check `is None`, not truthiness.
    """
    if not text:
        return None
    cleaned = _CURRENCY_PATTERN.sub('', text)
    match = _NUMBER_PATTERN.search(cleaned)
    if not match:
        return None
    number_str = match.group().replace(',', '')
    try:
        return float(number_str)
    except ValueError:
        return None


def extract_all_currency_values(text: str) -> list[float]:
    """Extracts ALL currency numbers in a string (for two-value queries like CAGR-solve)."""
    cleaned = _CURRENCY_PATTERN.sub('', text)
    matches = _NUMBER_PATTERN.findall(cleaned)
    values = []
    for m in matches:
        try:
            values.append(float(m.replace(',', '')))
        except ValueError:
            continue
    return values


def extract_percentage(text: str) -> float | None:
    """Extracts percentage as a decimal (7.5% -> 0.075). Applies decline sign automatically."""
    match = _PERCENT_PATTERN.search(text)
    if not match:
        return None
    value = float(match.group(1)) / 100
    if _DECLINE_KEYWORDS.search(text) and value > 0:
        value = -value  # "loses 5%" -> -0.05, even if user didn't type a minus sign
    return value

def extract_all_percentages(text: str) -> list[float]:
    """Extracts ALL percentages as decimals."""
    matches = _PERCENT_PATTERN.findall(text)
    values = []
    for m in matches:
        try:
            values.append(float(m) / 100)
        except ValueError:
            continue
    return values


def extract_years(text: str) -> float | None:
    match = _YEARS_PATTERN.search(text)
    return float(match.group(1)) if match else None


def extract_compounding_frequency(text: str) -> int:
    """Maps compounding phrasing to n. Defaults to 1 (annual) if unspecified."""
    text_lower = text.lower()
    if 'quarterly' in text_lower:
        return 4
    if 'monthly' in text_lower:
        return 12
    if 'semi-annual' in text_lower or 'semiannual' in text_lower or 'half-yearly' in text_lower:
        return 2
    if 'daily' in text_lower:
        return 365
    return 1


# ---------- FINANCIAL FORMULAS ----------

def compound_interest(principal: float, annual_rate: float, years: float,
                       compounds_per_year: int = 1) -> float:
    """FV = P * (1 + r/n)^(n*t). Rate is decimal (0.075 for 7.5%), can be negative."""
    if principal is None or annual_rate is None or years is None:
        raise ValueError("Missing required value for compound interest calculation")
    return principal * (1 + annual_rate / compounds_per_year) ** (compounds_per_year * years)


def percentage_of(value: float, percent: float) -> float:
    """Returns percent% of value. percent is a whole number (15 for 15%), not decimal."""
    if value is None or percent is None:
        raise ValueError("Missing value for percentage_of calculation")
    return value * (percent / 100)


def percentage_change(old_value: float, new_value: float) -> float:
    """Returns % change from old_value to new_value. Raises on old_value == 0."""
    if old_value is None or new_value is None:
        raise ValueError("Missing value for percentage_change calculation")
    if old_value == 0:
        raise ValueError("Cannot calculate percentage change when the old value is zero.")
    return ((new_value - old_value) / old_value) * 100


def cagr_solve(initial_value: float, final_value: float, years: float) -> float:
    """Solves for compound annual growth rate given start/end values and duration."""
    if initial_value is None or final_value is None or years is None:
        raise ValueError("Missing value for CAGR calculation")
    if initial_value <= 0 or years <= 0:
        raise ValueError("initial_value and years must be positive for CAGR")
    return ((final_value / initial_value) ** (1 / years) - 1) * 100


def sum_list(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values)


# ---------- ADDITIONAL FORMULAS (margin, DCF, WACC, YoY) ----------

def margin(revenue: float, profit: float) -> float:
    """Returns profit margin as a percentage. Works for gross/operating/net margin
    depending on what 'profit' value is passed in (gross profit, operating income, net income)."""
    if revenue is None or profit is None:
        raise ValueError("Missing value for margin calculation")
    if revenue == 0:
        raise ValueError("Cannot compute margin with zero revenue")
    return (profit / revenue) * 100


def yoy_growth(previous_value: float, current_value: float) -> float:
    """Year-over-year growth %. Same math as percentage_change but kept as a 
    separate named function since YoY queries have distinct phrasing 
    ('compared to last year', 'YoY growth') that the classifier should map here."""
    if previous_value is None or current_value is None:
        raise ValueError("Missing value for YoY calculation")
    if previous_value == 0:
        raise ValueError("Cannot compute YoY growth from a zero base value")
    return ((current_value - previous_value) / previous_value) * 100


def dcf(cash_flows: list[float], discount_rate: float, terminal_value: float = 0.0) -> float:
    """
    Discounted Cash Flow valuation. cash_flows are future projected flows 
    (year 1, year 2, ... — do NOT include a negative initial investment here, 
    that's what distinguishes DCF-as-valuation from NPV-as-investment-decision).
    terminal_value (optional) is discounted at the final period and added.
    """
    if not cash_flows:
        raise ValueError("No cash flows provided for DCF")
    if discount_rate is None:
        raise ValueError("Missing discount rate for DCF")
    n = len(cash_flows)
    pv_flows = sum(cf / (1 + discount_rate) ** (i + 1) for i, cf in enumerate(cash_flows))
    pv_terminal = terminal_value / (1 + discount_rate) ** n if terminal_value else 0.0
    return pv_flows + pv_terminal


def wacc(equity_value: float, debt_value: float, cost_of_equity: float,
         cost_of_debt: float, tax_rate: float) -> float:
    """
    Weighted Average Cost of Capital, as a percentage.
    cost_of_equity, cost_of_debt, tax_rate should all be decimals (0.08, not 8).
    """
    if None in (equity_value, debt_value, cost_of_equity, cost_of_debt, tax_rate):
        raise ValueError("Missing value for WACC calculation")
    total_value = equity_value + debt_value
    if total_value == 0:
        raise ValueError("Equity + debt cannot both be zero for WACC")
    equity_weight = equity_value / total_value
    debt_weight = debt_value / total_value
    result = (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt * (1 - tax_rate))
    return result * 100


def npv(cash_flows: list[float], discount_rate: float) -> float:
    """cash_flows[0] is the initial investment (negative), rest are inflows."""
    if not cash_flows:
        raise ValueError("No cash flows provided")
    return sum(cf / (1 + discount_rate) ** i for i, cf in enumerate(cash_flows))

def strip_currency_and_commas(text: str) -> str:
    """Legacy backward compatibility method for basic math node."""
    cleaned = re.sub(r'(?i)\b(?:rs|inr|usd)\b\.?\s?|[₹$]', '', text)
    return cleaned.replace(',', '')
