# modules/refinement.py
from typing import Any

# TODO: The reward functions should be replaced with more sophisticated logic as needed.
# They currently serve as simple examples. Just for formation and testing.
# You would not like one out of budguet right?

# Reward: prefer generations that surface a usable budget rather than vague placeholders.
def reward_budget_present(inputs: dict[str, Any], pred) -> float:
    budget = (pred.estimated_budget or "").strip().lower()
    if not budget or budget in ["n/a", "unknown", "tbd", "not provided", "not specified"]:
        return -1.0
    return 1.0


# Reward: ensure the refinement output respects the compliance schema (bool + string types).
def reward_compliance_schema(inputs: dict[str, Any], pred) -> float:
    if not isinstance(pred.is_compliant, bool):
        return -1.0
    if not isinstance(pred.rejection_reason, str):
        return -1.0
    return 1.0
