"""
Math Solver node. Split responsibility:
- LLM: classifies which formula applies (small, low-error task)
- Python: extracts every number deterministically via calculator.py (never LLM)
"""
from tools.calculator import (
    normalize_currency, extract_all_currency_values, extract_percentage,
    extract_all_percentages,
    extract_years, extract_compounding_frequency, compound_interest,
    percentage_of, percentage_change, cagr_solve, npv,
    margin, yoy_growth, dcf, wacc
)
from core.db import chat

FORMULA_CLASSIFICATION_PROMPT = """
Classify this financial math question into exactly ONE category. Reply with 
ONLY the category name, nothing else.

Categories:
- compound_interest: investing/growing/losing money over time at a rate
- percentage_of: "what is X% of Y"
- percentage_change: "changed from X to Y, what's the % change"
- cagr_solve: "invested X, now worth Y, what's the growth rate" (SOLVING FOR rate)
- yoy_growth: "compared to last year", "year-over-year growth", explicitly annual comparison
- margin: gross/operating/net margin, "what % of revenue is profit"
- dcf: discounted cash flow valuation with projected future cash flows and a discount rate
- npv: net present value with an initial investment (negative) plus inflows and a discount rate
- wacc: weighted average cost of capital, given equity, debt, cost of equity/debt, tax rate
- unknown: doesn't match any above

Question: {query}
Category:
"""

def classify_formula(query: str) -> str:
    response = chat.invoke(FORMULA_CLASSIFICATION_PROMPT.format(query=query))
    return response.content.strip().lower()


def solve_math(state):
    print("---NODE: MATH SOLVER---")
    query = state["current_question"]
    formula = classify_formula(query)

    try:
        if formula == "compound_interest":
            rate = extract_percentage(query)
            years = extract_years(query)
            n = extract_compounding_frequency(query)

            import re
            # Remove percentages and years from the string so they aren't mistaken for the principal
            cleaned_query = re.sub(r'(-?\d+\.?\d*)\s*%', '', query)
            cleaned_query = re.sub(r'(\d+\.?\d*)\s*(?:years?|yrs?)', '', cleaned_query, flags=re.IGNORECASE)
            principal = normalize_currency(cleaned_query)

            if principal is None or rate is None or years is None:
                return {"draft_answer": (
                    "I couldn't extract the principal amount, rate, or duration "
                    "clearly from your question. Could you rephrase with explicit "
                    "numbers, e.g. 'invest ₹100000 at 8% for 5 years'?"
                )}

            result = compound_interest(principal, rate, years, n)
            return {"draft_answer": f"The future value would be approximately ₹{result:,.2f}."}

        elif formula == "percentage_of":
            values = extract_all_currency_values(query)
            percent_match = extract_percentage(query)
            # percentage_of expects percent as whole number, extract_percentage returns decimal
            percent = percent_match * 100 if percent_match is not None else None
            if not values or percent is None:
                return {"draft_answer": "I couldn't extract the numbers needed for this percentage calculation."}
            result = percentage_of(values[0], percent)
            return {"draft_answer": f"The result is {result:,.2f}."}

        elif formula == "percentage_change":
            values = extract_all_currency_values(query)
            if len(values) < 2:
                return {"draft_answer": "I need two values (old and new) to compute a percentage change."}
            result = percentage_change(values[0], values[1])
            direction = "increase" if result >= 0 else "decrease"
            return {"draft_answer": f"That's a {abs(result):.2f}% {direction}."}

        elif formula == "cagr_solve":
            values = extract_all_currency_values(query)
            years = extract_years(query)
            if len(values) < 2 or years is None:
                return {"draft_answer": "I need the initial value, final value, and duration in years to compute CAGR."}
            result = cagr_solve(values[0], values[1], years)
            return {"draft_answer": f"The compound annual growth rate is approximately {result:.2f}%."}

        elif formula == "npv":
            values = extract_all_currency_values(query)
            percents = extract_all_percentages(query)
            if not values or not percents:
                return {"draft_answer": (
                    "For NPV, please provide your cash flows in order and the discount rate as a percentage."
                )}
            discount_rate = percents[0]
            result = npv(values, discount_rate)
            return {"draft_answer": f"The Net Present Value (NPV) is approximately ₹{result:,.2f}."}

        elif formula == "yoy_growth":
            values = extract_all_currency_values(query)
            if len(values) < 2:
                return {"draft_answer": "I need last year's value and this year's value to compute YoY growth."}
            result = yoy_growth(values[0], values[1])
            direction = "growth" if result >= 0 else "decline"
            return {"draft_answer": f"That's a {abs(result):.2f}% year-over-year {direction}."}

        elif formula == "margin":
            values = extract_all_currency_values(query)
            if len(values) < 2:
                return {"draft_answer": "I need both the revenue and profit figures to compute margin."}
            result = margin(values[0], values[1])
            return {"draft_answer": f"The margin is {result:.2f}%."}

        elif formula in ("dcf", "wacc"):
            # These need multiple structured inputs (cash flow lists, multiple 
            # rates) that plain regex extraction can't reliably disambiguate 
            # from free text. Ask the user for structured input rather than 
            # guess — wrong DCF/WACC numbers are worse than asking a follow-up.
            if formula == "dcf":
                return {"draft_answer": (
                    "For a DCF valuation, please provide the projected cash "
                    "flows as a list (e.g. [5000, 6000, 7000]), the discount "
                    "rate, and optionally a terminal value."
                )}
            else:
                return {"draft_answer": (
                    "For WACC, please provide: equity value, debt value, "
                    "cost of equity, cost of debt, and tax rate."
                )}

        else:
            return {"draft_answer": "I couldn't identify what calculation you're asking for. Could you rephrase?"}

    except ValueError as e:
        return {"draft_answer": f"I couldn't complete this calculation: {e}"}
