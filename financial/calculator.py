from typing import Union, List

def calculate_yoy_growth(current: float, previous: float) -> float:
    """Calculates Year-over-Year percentage growth."""
    if previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100.0

def calculate_cagr(beginning_value: float, ending_value: float, num_years: float) -> float:
    """Calculates Compound Annual Growth Rate."""
    if beginning_value <= 0 or num_years <= 0:
        return 0.0
    return ((ending_value / beginning_value) ** (1 / num_years) - 1) * 100.0

def calculate_margin(profit: float, revenue: float) -> float:
    """Calculates profit margin as a percentage."""
    if revenue == 0:
        return 0.0
    return (profit / revenue) * 100.0

def calculate_absolute_difference(val1: float, val2: float) -> float:
    """Calculates absolute difference."""
    return abs(val1 - val2)

def calculate_sum(values: List[float]) -> float:
    """Calculates sum of a list of values."""
    return sum(values)

def calculate_npv(discount_rate: float, cash_flows: List[float]) -> float:
    """
    Calculates Net Present Value.
    cash_flows: List where index 0 is typically the initial investment (negative), followed by future cash flows.
    discount_rate: The rate as a decimal (e.g., 0.10 for 10%)
    """
    npv = 0.0
    for t, cf in enumerate(cash_flows):
        npv += cf / ((1 + discount_rate) ** t)
    return npv

def calculate_dcf(discount_rate: float, cash_flows: List[float], terminal_value: float) -> float:
    """
    Calculates Discounted Cash Flow including a terminal value.
    """
    dcf = 0.0
    # Discount projected cash flows
    for t, cf in enumerate(cash_flows, start=1):
        dcf += cf / ((1 + discount_rate) ** t)
    # Discount terminal value
    t_final = len(cash_flows)
    dcf += terminal_value / ((1 + discount_rate) ** t_final)
    return dcf

def calculate_wacc(equity: float, debt: float, cost_of_equity: float, cost_of_debt: float, tax_rate: float) -> float:
    """
    Calculates Weighted Average Cost of Capital (WACC).
    equity: Total market value of equity
    debt: Total market value of debt
    cost_of_equity: Cost of equity as decimal
    cost_of_debt: Cost of debt as decimal
    tax_rate: Corporate tax rate as decimal
    """
    total_value = equity + debt
    if total_value == 0:
        return 0.0
    weight_equity = equity / total_value
    weight_debt = debt / total_value
    
    wacc = (weight_equity * cost_of_equity) + (weight_debt * cost_of_debt * (1 - tax_rate))
    return wacc
