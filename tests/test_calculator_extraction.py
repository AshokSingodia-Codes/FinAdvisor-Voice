import pytest
from tools.calculator import (
    normalize_currency, extract_percentage, extract_years,
    extract_compounding_frequency, compound_interest, cagr_solve,
)

CURRENCY_CASES = [
    ("₹1,00,000", 100000.0),
    ("Rs. 5,00,000", 500000.0),
    ("₹1,25,00,000 (1.25 crore)", 12500000.0),
    ("₹0", 0.0),
    ("$10,000", 10000.0),
    ("₹2,00,000", 200000.0),
    ("Rs 75,000", 75000.0),
]

@pytest.mark.parametrize("text,expected", CURRENCY_CASES)
def test_normalize_currency(text, expected):
    assert normalize_currency(text) == expected

PERCENT_CASES = [
    ("7.5% annual compound interest", 0.075),
    ("loses 5% annually", -0.05),      # decline keyword flips sign
    ("grows at 9% annually", 0.09),
    ("declining 10%", -0.10),
]

@pytest.mark.parametrize("text,expected", PERCENT_CASES)
def test_extract_percentage(text, expected):
    assert abs(extract_percentage(text) - expected) < 1e-9

def test_compound_interest_zero_principal():
    assert compound_interest(0, 0.10, 5) == 0

def test_compound_interest_negative_rate():
    result = compound_interest(200000, -0.05, 3)
    assert abs(result - 171475.0) < 1  # ₹2,00,000 declining 5%/yr for 3yr

def test_cagr_solve():
    result = cagr_solve(75000, 95000, 2)
    assert abs(result - 12.54) < 0.1

def test_compounding_frequency():
    assert extract_compounding_frequency("compounded quarterly") == 4
    assert extract_compounding_frequency("invest at 8% for 5 years") == 1
