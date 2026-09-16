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
