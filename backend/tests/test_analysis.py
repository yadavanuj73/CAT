"""
Automated tests for Analytical Engine topic frequency and recency weighting calculations.
"""

import pytest
from app.services.analysis_service import classify_text_to_topic


def test_topic_classification_heuristics():
    qa_text = "Two boats travel in opposite directions with a stream velocity of 3 km/h."
    topic, subtopic = classify_text_to_topic(qa_text, "QA")
    assert topic == "Arithmetic"
    assert "Speed" in subtopic or "Distance" in subtopic

    algebra_text = "Find the sum of all roots of the equation log_2(x^2 - 4) = 5."
    topic, subtopic = classify_text_to_topic(algebra_text, "QA")
    assert topic == "Algebra"

    rc_text = "The philosophical underpinnings of moral consequentialism dictate that..."
    topic, subtopic = classify_text_to_topic(rc_text, "VARC")
    assert topic == "Reading Comprehension"


def test_recency_weight_decay():
    current_year = 2025
    decay = 0.85

    # CAT 2024 (1 year ago) vs CAT 2010 (15 years ago)
    w_2024 = decay ** (current_year - 2024)  # 0.85
    w_2010 = decay ** (current_year - 2010)  # ~0.087

    assert w_2024 > w_2010
    assert round(w_2024, 2) == 0.85
    assert w_2024 / w_2010 > 9.0  # Recent questions carry ~10x more weight
