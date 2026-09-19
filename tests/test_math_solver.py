import pytest
from tools.calculator import strip_currency_and_commas, compound_interest

def test_strip_currency_and_commas_indian():
    assert strip_currency_and_commas("₹1,00,000") == "100000"
    assert strip_currency_and_commas("Rs. 12,50,000") == "1250000"
    assert strip_currency_and_commas("1,00,00,000") == "10000000"

def test_strip_currency_and_commas_western():
    assert strip_currency_and_commas("$1,000,000") == "1000000"
    assert strip_currency_and_commas("The price is $1,234.56") == "The price is 1234.56"

def test_strip_currency_and_commas_no_change():
    assert strip_currency_and_commas("No numbers here.") == "No numbers here."
    assert strip_currency_and_commas("100000") == "100000"

def test_compound_interest():
    # 1,00,000 at 8% for 5 years
    fv = compound_interest(100000, 0.08, 5, 1)
    # Expected: 100000 * 1.08^5 = 146932.80768
    assert abs(fv - 146932.80) < 1.0

def test_compound_interest_monthly():
    fv = compound_interest(100000, 8, 5, 12)
    assert fv > 146932.80 # Monthly compounding should be higher than annual
