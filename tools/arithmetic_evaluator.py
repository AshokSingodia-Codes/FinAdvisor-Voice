"""
Deterministic arithmetic evaluator backward-compatibility bridge to tools.fast_math.
"""
from tools.fast_math import (
    try_evaluate_fast_math as try_evaluate_pure_arithmetic,
    format_indian_number,
    format_western_number,
    format_final_result as format_arithmetic_result
)

__all__ = [
    "try_evaluate_pure_arithmetic",
    "format_arithmetic_result",
    "format_indian_number",
    "format_western_number",
]

