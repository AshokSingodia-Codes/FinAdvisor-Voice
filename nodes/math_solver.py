"""
Math Solver node. Split responsibility:
- LLM: classifies which formula applies (small, low-error task)
- Python: extracts every number deterministically via calculator.py (never LLM)
"""
from tools.calculator import (
    normalize_currency, extract_all_currency_values, extract_percentage,
    extract_all_percentages,
    extract_years, extract_compounding_frequency, compound_interest, sip_future_value,
    percentage_of, percentage_change, cagr_solve, npv,
    margin, yoy_growth, dcf, wacc,
    calculate_income_tax_new_regime, calculate_income_tax_old_regime,
    compare_tax_regimes, calculate_capital_gains_tax
)
from core.db import fast_chat

FORMULA_CLASSIFICATION_PROMPT = """
Classify this financial math question into exactly ONE category. Reply with 
ONLY the category name, nothing else.

Categories:
- income_tax: calculating Indian income tax on a salary/income, comparing new vs old tax regime
- capital_gains: calculating capital gains tax on selling stocks, mutual funds, property, gold, or crypto
- sip: monthly regular investing, systematic investment plan, "₹X monthly for Y years at Z% return"
- compound_interest: lump sum investing/growing/losing money over time at a rate
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
    try:
        response = fast_chat.invoke(FORMULA_CLASSIFICATION_PROMPT.format(query=query))
        cat = response.content.strip().lower()
        if cat in [
            "income_tax", "capital_gains", "sip", "compound_interest",
            "percentage_of", "percentage_change", "cagr_solve",
            "yoy_growth", "margin", "dcf", "npv", "wacc"
        ]:
            return cat
    except Exception as e:
        print(f"[math_solver] Formula classification fallback due to: {e}")

    # Deterministic heuristic fallback
    q = query.lower()
    if "sip" in q or ("monthly" in q and "invest" in q):
        return "sip"
    if "cagr" in q or "growth rate" in q:
        return "cagr_solve"
    if "tax" in q or "regime" in q:
        return "income_tax"
    if "capital gain" in q or "ltcg" in q or "stcg" in q:
        return "capital_gains"
    if "yoy" in q or "year-over-year" in q:
        return "yoy_growth"
    if "margin" in q:
        return "margin"
    if "npv" in q:
        return "npv"
    if "dcf" in q:
        return "dcf"
    if "wacc" in q:
        return "wacc"
    if "%" in q or "percent" in q:
        if "change" in q or ("from" in q and "to" in q):
            return "percentage_change"
        return "percentage_of"
    if "interest" in q or "compound" in q:
        return "compound_interest"
    return "unknown"


def solve_math(state):
    print("---NODE: MATH SOLVER---")
    query = state.get("current_question", state.get("original_question", ""))
    try:
        formula = classify_formula(query)
        if formula == "sip" or ("monthly" in query.lower() and "sip" in query.lower()):
            rate = extract_percentage(query)
            years = extract_years(query)

            import re
            cleaned_query = re.sub(r'(-?\d+\.?\d*)\s*%', '', query)
            cleaned_query = re.sub(r'(\d+\.?\d*)\s*(?:years?|yrs?)', '', cleaned_query, flags=re.IGNORECASE)
            monthly_inv = normalize_currency(cleaned_query)

            if monthly_inv is None or rate is None or years is None:
                return {"draft_answer": (
                    "I couldn't extract the monthly amount, expected rate, or duration "
                    "clearly from your question. Could you rephrase with explicit "
                    "numbers, e.g. '₹5,000 monthly SIP for 10 years at 12% return'?"
                )}

            fv = sip_future_value(monthly_inv, rate, years)
            total_invested = monthly_inv * (years * 12)
            wealth_gain = fv - total_invested
            return {"draft_answer": (
                f"### 📊 Systematic Investment Plan (SIP) Projection\n\n"
                f"* **Monthly SIP Amount**: ₹{monthly_inv:,.2f}\n"
                f"* **Expected Return (CAGR)**: {rate * 100:.1f}%\n"
                f"* **Investment Duration**: {years:.0f} years ({years * 12:.0f} monthly installments)\n\n"
                f"**Financial Breakdown**:\n"
                f"* **Total Capital Invested**: ₹{total_invested:,.2f}\n"
                f"* **Estimated Wealth Gained**: ₹{wealth_gain:,.2f}\n"
                f"* **Total Future Value**: **₹{fv:,.2f}**\n\n"
                f"> 💡 *Financial Advisor Insight: A ₹{monthly_inv:,.0f} monthly SIP over {years:.0f} years at {rate*100:.0f}% CAGR generates ₹{wealth_gain:,.0f} in compounding gains on top of your ₹{total_invested:,.0f} invested.*"
            )}

        elif formula == "compound_interest":
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

    except Exception as e:
        print(f"[math_solver error]: {e}")
        return {"draft_answer": f"I couldn't complete this calculation. Please specify the numbers clearly, or ask your question with details."}
