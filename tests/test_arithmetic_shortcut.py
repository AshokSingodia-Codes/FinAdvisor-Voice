import pytest
from tools.arithmetic_evaluator import try_evaluate_pure_arithmetic, format_arithmetic_result
from nodes.math_calculation import do_math_calculation
from nodes.router import route_question
from tools.calculator import safe_calculate

def test_order_of_operations():
    # 4+4*2 should equal 12 (not 16)
    is_arith, ans, res = try_evaluate_pure_arithmetic("4+4*2")
    assert is_arith is True
    assert res == 12.0
    assert "12" in ans

    # Parentheses override precedence: (4+4)*2 = 16
    is_arith, ans, res = try_evaluate_pure_arithmetic("(4+4)*2")
    assert is_arith is True
    assert res == 16.0
    assert "16" in ans

    # 2*4*8+150 = 64 + 150 = 214
    is_arith, ans, res = try_evaluate_pure_arithmetic("2*4*8+150")
    assert is_arith is True
    assert res == 214.0
    assert "214" in ans


def test_division_and_multiplication():
    # 8/2 = 4
    is_arith, ans, res = try_evaluate_pure_arithmetic("8/2")
    assert is_arith is True
    assert res == 4.0
    assert "4" in ans

    # 2*2 = 4
    is_arith, ans, res = try_evaluate_pure_arithmetic("2*2")
    assert is_arith is True
    assert res == 4.0
    assert "4" in ans

    # Chained division 100 / 4 / 5 = 5
    is_arith, ans, res = try_evaluate_pure_arithmetic("100/4/5")
    assert is_arith is True
    assert res == 5.0
    assert "5" in ans


def test_large_numbers_and_decimals():
    # Large number addition regression test
    is_arith, ans, res = try_evaluate_pure_arithmetic("2000892+3")
    assert is_arith is True
    assert res == 2000895.0
    assert "2,000,895" in ans

    # Decimal arithmetic
    is_arith, ans, res = try_evaluate_pure_arithmetic("12.5 * 4 + 0.5")
    assert is_arith is True
    assert res == 50.5
    assert "50.5" in ans


def test_percentage_patterns():
    # 5% of 2020 = 101
    is_arith, ans, res = try_evaluate_pure_arithmetic("5% of 2020")
    assert is_arith is True
    assert res == 101.0
    assert "101" in ans

    # 18% of 50000 = 9000
    is_arith, ans, res = try_evaluate_pure_arithmetic("18% of 50000")
    assert is_arith is True
    assert res == 9000.0
    assert "9,000" in ans

    # 12.5 percent of 800 = 100
    is_arith, ans, res = try_evaluate_pure_arithmetic("12.5 percent of 800")
    assert is_arith is True
    assert res == 100.0
    assert "100" in ans


def test_power_and_unary_operators():
    # 2^3 = 8
    is_arith, ans, res = try_evaluate_pure_arithmetic("2^3")
    assert is_arith is True
    assert res == 8.0
    assert "8" in ans

    # Negative unary
    is_arith, ans, res = try_evaluate_pure_arithmetic("-10 + 25")
    assert is_arith is True
    assert res == 15.0
    assert "15" in ans


def test_division_by_zero_and_malformed_queries_fall_through():
    # Division by zero should safely return (False, None, None)
    is_arith, ans, res = try_evaluate_pure_arithmetic("8/0")
    assert is_arith is False
    assert ans is None

    # Malformed syntax should safely return (False, None, None)
    is_arith, ans, res = try_evaluate_pure_arithmetic("4++*2")
    assert is_arith is False
    assert ans is None


def test_non_arithmetic_queries_rejected():
    # Financial word problems must NOT be matched by pure arithmetic shortcut
    financial_queries = [
        "calculate tax on 15 lakh income",
        "SIP of 10000 monthly for 5 years at 12%",
        "Reliance share price",
        "what is WACC formula",
        "Apple revenue in 2024",
        "What was the total gross merchandise volume of Cyberdyne Systems in 2020?"
    ]
    for q in financial_queries:
        is_arith, _, _ = try_evaluate_pure_arithmetic(q)
        assert is_arith is False, f"Financial query '{q}' should not be matched by pure arithmetic shortcut"


def test_bare_year_in_factual_question_not_caught_by_fast_path():
    """
    REGRESSION TEST — fast-path false positive (found via eval_trap_questions.py).

    Problem shape: a real factual question contains an isolated year (e.g. "2020") or
    other bare number with NO arithmetic operator (+, -, *, /, %). The fast-path gate
    must NOT treat the embedded number as a complete arithmetic expression.

    Correct behaviour: is_math=False, answer=None — the query falls through to the
    graph/LLM pipeline so it can be answered (or safely refused) properly.

    Failure mode: returning is_math=True with a fabricated bare number as the answer,
    bypassing the RAG/LLM pipeline entirely — a hallucination-adjacent bug.
    """
    bare_number_factual_queries = [
        # Original failing case — fictional company + year, no operator
        "What was the total gross merchandise volume of Cyberdyne Systems in 2020?",
        # Variants of the same shape: year embedded in a real question
        "What was Apple's revenue in 2024?",
        "How much did Reliance earn in FY2023?",
        "What was HDFC Bank's net profit in Q3 2022?",
        "Tell me Infosys's headcount as of 2021",
        # Bare year alone — not arithmetic
        "2020",
        "FY2024",
        "Q3 2023",
        # Year with context words but still no operator
        "revenue 2020",
        "total 2020",
        "volume of 2020",
        "What is total 2020",
        "EBITDA in FY2020",
    ]
    for q in bare_number_factual_queries:
        is_arith, ans, val = try_evaluate_pure_arithmetic(q)
        assert is_arith is False, (
            f"REGRESSION: factual query containing a bare year/number was caught by "
            f"the fast-path gate.\n"
            f"  Query : {q!r}\n"
            f"  Answer: {ans!r}\n"
            f"  Value : {val!r}\n"
            f"A bare number with no arithmetic operator must NOT trigger the fast path."
        )


def test_do_math_calculation_fast_path():
    state = {"current_question": "2*4*8+150"}
    res = do_math_calculation(state)
    assert "214" in res["draft_answer"]

    state2 = {"current_question": "8/2"}
    res2 = do_math_calculation(state2)
    assert "4" in res2["draft_answer"]


def test_router_fast_path_for_pure_arithmetic():
    state = {"original_question": "2000892+3", "memory_context": ""}
    res = route_question(state)
    assert res["routing_decision"] == "math_calculation"
