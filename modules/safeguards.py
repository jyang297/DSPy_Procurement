# modules/safeguards.py
import dspy

from modules.signatures import ComplianceSignature


class ContractComplianceChecker(dspy.Module):
    def __init__(self):
        super().__init__()
        self.check = dspy.Predict(ComplianceSignature)

    def forward(self, draft_terms: str, compliance_rules: str):
        return self.check(
            draft_terms=draft_terms,
            compliance_rules=compliance_rules,
        )
