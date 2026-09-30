"""
Comprehensive Unit Tests for Unified Fast-Math Engine (Categories A through M).
Tests all deterministic math shortcuts, formatting, Indian/Western currencies,
statistics, date math, multi-step math, and graceful error handling.
"""
import pytest
from tools.fast_math import (
    try_evaluate_fast_math,
    format_indian_number,
    format_western_number,
    detect_currency_and_style,
    normalize_words_to_math_expression
)
from nodes.math_calculation import do_math_calculation
from nodes.router import route_question


# =============================================================================
# CATEGORY A — Pure Arithmetic Expressions
# =============================================================================

def test_category_a_pure_arithmetic():
    # Precedence & basic ops
    assert try_evaluate_fast_math("2*4*8+150")[2] == 214.0
    assert try_evaluate_fast_math("8/2")[2] == 4.0
    assert try_evaluate_fast_math("(4+4)*2")[2] == 16.0
    assert try_evaluate_fast_math("4+4*2")[2] == 12.0
    assert try_evaluate_fast_math("17654487464+64465454")[2] == 17718952918.0
    assert try_evaluate_fast_math("2000892+3")[2] == 2000895.0


# =============================================================================
# CATEGORY B — Percentages, Ratios, Fractions, Discounts
# =============================================================================

def test_category_b_percentages_and_ratios():
    # Percentage of
    is_math, ans, val = try_evaluate_fast_math("5% of 2020")
    assert is_math is True
    assert val == 101.0
    assert "101" in ans

    # Fraction of
    is_math, ans, val = try_evaluate_fast_math("3/4 of 500")
    assert is_math is True
    assert val == 375.0
    assert "375" in ans

    # Discount
    is_math, ans, val = try_evaluate_fast_math("what's a 20% discount on 1200")
    assert is_math is True
    assert val == 960.0
    assert "960" in ans

    # Ratio split
    is_math, ans, val = try_evaluate_fast_math("split 900 in a 2:3 ratio")
    assert is_math is True
    assert "360" in ans  # 900 * 2/5 = 360
    assert "540" in ans  # 900 * 3/5 = 540


# =============================================================================
# CATEGORY C — Number Words instead of Digits
# =============================================================================

def test_category_c_number_words():
    # Two plus two
    is_math, ans, val = try_evaluate_fast_math("what is two plus two")
    assert is_math is True
    assert val == 4.0
    assert "4" in ans

    # Multiply five by six
    is_math, ans, val = try_evaluate_fast_math("multiply five by six")
    assert is_math is True
    assert val == 30.0
    assert "30" in ans

    # Twenty five minus ten
    is_math, ans, val = try_evaluate_fast_math("twenty five minus ten")
    assert is_math is True
    assert val == 15.0
    assert "15" in ans


# =============================================================================
# CATEGORY D & L — Currency & Indian Numbering System (Lakh / Crore)
# =============================================================================

def test_category_d_and_l_currencies_and_indian_numbering():
    # ₹50,000 + ₹12,000
    is_math, ans, val = try_evaluate_fast_math("₹50,000 + ₹12,000")
    assert is_math is True
    assert val == 62000.0
    assert "₹" in ans
    assert "62,000" in ans

    # $1,200 * 3
    is_math, ans, val = try_evaluate_fast_math("$1,200 * 3")
    assert is_math is True
    assert val == 3600.0
    assert "$" in ans
    assert "3,600" in ans

    # 5 lakh + 2.5 lakh -> ₹7,50,000
    is_math, ans, val = try_evaluate_fast_math("5 lakh + 2.5 lakh")
    assert is_math is True
    assert val == 750000.0
    assert "7,50,000" in ans

    # Indian comma formatting helper test
    assert format_indian_number(750000, "₹") == "₹7,50,000"
    assert format_indian_number(12500000, "₹") == "₹1,25,00,000"


# =============================================================================
# CATEGORY E — Statistics over a List of Numbers
# =============================================================================

def test_category_e_statistics():
    # Average of returns
    is_math, ans, val = try_evaluate_fast_math("average of 12%, 8%, 16%, 4%")
    assert is_math is True
    assert val == 10.0
    assert "10.00%" in ans

    # Median
    is_math, ans, val = try_evaluate_fast_math("median of 500, 700, 300, 900")
    assert is_math is True
    assert val == 600.0
    assert "600" in ans

    # Standard deviation
    is_math, ans, val = try_evaluate_fast_math("standard deviation of 10, 12, 9, 14, 11")
    assert is_math is True
    assert val is not None
    assert "Standard Deviation" in ans


# =============================================================================
# CATEGORY G — Date / Tenure-Based Calculations
# =============================================================================

def test_category_g_date_tenure_math():
    # Age projection
    is_math, ans, val = try_evaluate_fast_math("how old will I be in 2040 if I'm 24 now")
    assert is_math is True
    assert val is not None
    assert "years old" in ans

    # 5-year FD maturity
    is_math, ans, val = try_evaluate_fast_math("if I invest today, what year does a 5-year FD mature")
    assert is_math is True
    assert val is not None
    assert "mature in" in ans

    # Days until date
    is_math, ans, val = try_evaluate_fast_math("how many days until 15 March 2027")
    assert is_math is True
    assert val is not None
    assert "days remaining" in ans or "days ago" in ans


# =============================================================================
# CATEGORY J — Multi-step / Nested Calculations
# =============================================================================

def test_category_j_sequential_calculations():
    # "calculate 12% of 50000, then add 8% of that result"
    # Step 1: 12% of 50000 = 6000
    # Step 2: 6000 + (8% of 6000) = 6000 + 480 = 6480
    is_math, ans, val = try_evaluate_fast_math("calculate 12% of 50000, then add 8% of that result")
    assert is_math is True
    assert val == 6480.0
    assert "6,480" in ans


# =============================================================================
# CATEGORY M — Malformed & Edge Cases
# =============================================================================

def test_category_m_edge_cases():
    # Division by zero
    is_math, ans, val = try_evaluate_fast_math("8/0")
    assert is_math is True
    assert "Division by zero is undefined" in ans
    assert val is None

    # Unbalanced / garbage input -> fall through safely
    is_math, ans, val = try_evaluate_fast_math("2+*3")
    assert is_math is False
    assert ans is None

    # Overflow limit guard
    is_math, ans, val = try_evaluate_fast_math("10^25")
    assert is_math is True
    assert "computational limit" in ans


# =============================================================================
# Integration with Nodes
# =============================================================================

def test_nodes_integration():
    # Router fast-path
    route_res = route_question({"original_question": "4+4*2", "memory_context": ""})
    assert route_res["routing_decision"] == "math_calculation"

    # Math calculation node execution
    node_res = do_math_calculation({"current_question": "₹50,000 + ₹12,000"})
    assert "62,000" in node_res["draft_answer"]
