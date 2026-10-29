import pytest
from core.domain_guardrails import is_out_of_domain_query, check_output_guardrail, FINANCIAL_GUARDRAIL_REFUSAL

def test_code_generation_guardrail_triggers():
    code_queries = [
        "write python code to sum two numbers",
        "give me python code of sum of two number",
        "python code to add 2 numbers",
        "write a python script to download data",
        "solve bubble sort in python",
        "create a function in python to reverse string",
        "def sum_two_numbers(a, b):",
        "write java code for binary search",
        "write a program to print fibonacci series",
        "give me code of sum",
        "python program to multiply matrices"
    ]
    for q in code_queries:
        is_violation, refusal = is_out_of_domain_query(q)
        assert is_violation is True, f"Failed to block code query: {q}"
        assert refusal == FINANCIAL_GUARDRAIL_REFUSAL

def test_inventor_and_trivia_guardrail_triggers():
    trivia_queries = [
        "who is the inventor of computer",
        "who invented computer",
        "name of inventor of bulb",
        "inventor of telephone",
        "who invented python",
        "who discovered gravity",
        "father of computer",
        "how to bake a cake",
        "recipe for chicken biryani",
        "who is messi"
    ]
    for q in trivia_queries:
        is_violation, refusal = is_out_of_domain_query(q)
        assert is_violation is True, f"Failed to block trivia query: {q}"
        assert refusal == FINANCIAL_GUARDRAIL_REFUSAL

def test_financial_queries_allowed():
    fin_queries = [
        "what is the price of Reliance?",
        "calculate SIP for 10000 per month for 10 years at 12%",
        "tax on 15 lakh income under new regime",
        "what is WACC formula?",
        "explain Black Scholes model",
        "what is DCF valuation?",
        "who is Warren Buffett?",
        "who is Nirmala Sitharaman?",
        "difference between LTCG and STCG",
        "show me balance sheet items for TCS"
    ]
    for q in fin_queries:
        is_violation, _ = is_out_of_domain_query(q)
        assert is_violation is False, f"Falsely blocked financial query: {q}"

def test_check_output_guardrail():
    # Code block leak should be intercepted
    bad_output = "Sure, here is your code:\n```python\ndef sum(a, b):\n    return a + b\n```"
    is_clean, sanitized = check_output_guardrail(bad_output, "write python code")
    assert is_clean is False
    assert sanitized == FINANCIAL_GUARDRAIL_REFUSAL

    # Clean financial output should be untouched
    good_output = "**The total tax liability under the New Regime is ₹1,04,000.**"
    is_clean, sanitized = check_output_guardrail(good_output, "tax on 15 lakh")
    assert is_clean is True
    assert sanitized == good_output
