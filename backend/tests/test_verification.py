"""
Automated tests for Data Verification Engine & Mathematical Solver.
"""

from app.utils.math_solver import verify_arithmetic_statement


def test_deterministic_arithmetic_verification():
    # Valid explicit arithmetic statement
    valid_text = "A sum of 24 + 36 = 60 is distributed among participants."
    passed, msg = verify_arithmetic_statement(valid_text)
    assert passed is True

    # Invalid / contradictory arithmetic statement
    invalid_text = "If 15 * 4 = 75 in base 10, determine the variance."
    failed, err_msg = verify_arithmetic_statement(invalid_text)
    assert failed is False
    assert "Arithmetic contradiction" in err_msg


def test_no_arithmetic_statement():
    text = "Find the roots of the quadratic equation x^2 - 5x + 6 = 0."
    passed, msg = verify_arithmetic_statement(text)
    assert passed is True
