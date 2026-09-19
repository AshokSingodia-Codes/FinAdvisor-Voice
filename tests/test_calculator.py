import pytest
from tools.calculator import (
    safe_calculate, percentage_of, percentage_change, sum_list,
    margin, yoy_growth, dcf, wacc
)

def test_safe_calculate_basic_arithmetic():
    assert safe_calculate("2 + 3") == 5.0
    assert safe_calculate("10 - 4") == 6.0
    assert safe_calculate("5 * 6") == 30.0
    assert safe_calculate("20 / 4") == 5.0
    assert safe_calculate("10 % 3") == 1.0

def test_safe_calculate_precedence_and_parentheses():
    assert safe_calculate("2 + 3 * 4") == 14.0
    assert safe_calculate("(2 + 3) * 4") == 20.0
    assert safe_calculate("10 / (2 + 3)") == 2.0

def test_safe_calculate_negative_numbers():
    assert safe_calculate("-5 + 10") == 5.0
    assert safe_calculate("10 * -2") == -20.0
    assert safe_calculate("-(-5)") == 5.0
    assert safe_calculate("+5") == 5.0

def test_safe_calculate_floats():
    assert safe_calculate("2.5 + 3.5") == 6.0
    assert safe_calculate("10.0 / 4.0") == 2.5

def test_safe_calculate_multiple_expressions():
    assert safe_calculate("2+5, 10*15, 2/5") == (7.0, 150.0, 0.4)
    assert safe_calculate("1+1, 2+2") == (2.0, 4.0)

def test_safe_calculate_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        safe_calculate("10 / 0")
    with pytest.raises(ZeroDivisionError):
        safe_calculate("10 % 0")

def test_safe_calculate_malformed():
    with pytest.raises(ValueError):
        safe_calculate("2 + ")
    with pytest.raises(ValueError):
        safe_calculate("abc")
    with pytest.raises(ValueError):
        safe_calculate("2 + abc")

def test_safe_calculate_injection_prevention():
    with pytest.raises(ValueError):
        safe_calculate("__import__('os').system('ls')")
    with pytest.raises(ValueError):
        safe_calculate("open('/etc/passwd').read()")
    with pytest.raises(ValueError):
        safe_calculate("eval('2+2')")
    with pytest.raises(ValueError):
        safe_calculate("exec('x = 5')")

def test_percentage_of():
    assert percentage_of(50000, 15) == 7500.0
    assert percentage_of(100, 50) == 50.0
    assert percentage_of(200, 0) == 0.0
    assert percentage_of(0, 10) == 0.0
    assert percentage_of(100, -10) == -10.0

def test_percentage_change():
    assert percentage_change(100, 150) == 50.0
    assert percentage_change(100, 50) == -50.0
    assert percentage_change(200, 200) == 0.0
    
def test_percentage_change_zero():
    with pytest.raises(ValueError, match="Cannot calculate percentage change when the old value is zero."):
        percentage_change(0, 100)

def test_sum_list():
    assert sum_list([15000, 5000, 2000]) == 22000.0
    assert sum_list([1.5, 2.5]) == 4.0
    assert sum_list([]) == 0.0
    assert sum_list([-5, 10]) == 5.0

def test_margin():
    assert abs(margin(391035, 180683) - 46.21) < 0.1  # example revenue/gross profit

def test_yoy_growth():
    assert abs(yoy_growth(100000, 115000) - 15.0) < 0.01

def test_dcf():
    result = dcf([5000, 6000, 7000], 0.10, terminal_value=50000)
    assert result > 0  # sanity check on structure; exact value depends on formula convention

def test_wacc():
    result = wacc(equity_value=700000, debt_value=300000, cost_of_equity=0.12,
                  cost_of_debt=0.06, tax_rate=0.25)
    assert 8 < result < 11  # weighted blend should land in this range
