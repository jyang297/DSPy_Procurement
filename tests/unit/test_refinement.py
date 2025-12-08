import pytest

from modules import refinement


class DummyPrediction:
    def __init__(self, estimated_budget="", is_compliant=None, rejection_reason=None):
        self.estimated_budget = estimated_budget
        self.is_compliant = is_compliant
        self.rejection_reason = rejection_reason


@pytest.mark.parametrize(
    ("estimated_budget", "expected"),
    [
        ("50k-100k", 1.0),
        (" $10,000 ", 1.0),
        ("unknown", -1.0),
        ("", -1.0),
        ("   ", -1.0),
        ("tbd", -1.0),
    ],
)
def test_reward_budget_present_handles_missing_budget(estimated_budget, expected):
    pred = DummyPrediction(estimated_budget=estimated_budget)
    score = refinement.reward_budget_present({}, pred)
    assert score == expected


@pytest.mark.parametrize(
    ("is_compliant", "rejection_reason", "expected"),
    [
        (True, "all good", 1.0),
        (False, "missing clause", 1.0),
        ("yes", "string instead of bool", -1.0),
        (True, None, -1.0),
    ],
)
def test_reward_compliance_schema_validates_types(is_compliant, rejection_reason, expected):
    pred = DummyPrediction(
        estimated_budget="50k-100k",
        is_compliant=is_compliant,
        rejection_reason=rejection_reason,
    )
    score = refinement.reward_compliance_schema({}, pred)
    assert score == expected
