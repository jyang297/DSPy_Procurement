# modules/analysis.py
import dspy

from modules.signatures import RequirementSpecSignature


class RequirementAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(RequirementSpecSignature)

    def forward(self, raw_request: str, feedback: str = "none"):
        return self.predict(raw_request=raw_request, feedback=feedback)
