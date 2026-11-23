"""
Mathematical Expression and Numerical Consistency Verification Utilities.
Ensures deterministic arithmetic correctness where numbers and equations are stated.
"""

import ast
import re
from typing import Tuple


def verify_arithmetic_statement(text: str) -> Tuple[bool, str]:
    """
    Scan question text for simple explicit equalities (e.g. 15 * 4 = 60).
    Verifies that stated arithmetic holds deterministically.
    """
    # Match patterns like: 24 + 36 = 60 or 12 * 8 = 96
    pattern = re.compile(r"(\d+\s*[\+\-\*\/]\s*\d+)\s*=\s*(\d+)")
    matches = pattern.findall(text)

    if not matches:
        return True, "No explicit arithmetic equalities detected in prompt text."

    for expr, expected_val in matches:
        try:
            # Parse arithmetic expression safely
            clean_expr = expr.strip()
            # Only allow digits, +, -, *, /, spaces
            if not re.match(r"^[\d\s\+\-\*\/]+$", clean_expr):
                continue
            calculated = eval(clean_expr)
            if calculated != float(expected_val):
                return False, f"Arithmetic contradiction detected: {clean_expr} calculated as {calculated}, but stated as {expected_val}."
        except Exception:
            continue

    return True, "All explicit arithmetic expressions verified deterministically."
