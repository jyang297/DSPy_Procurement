# modules/safeguards.py
import dspy
from modules.signatures import ComplianceSignature
from config.business_rules import COMPLIANCE_RULES

class ContractComplianceChecker(dspy.Module):
    def __init__(self):
        super().__init__()
        self.check = dspy.Predict(ComplianceSignature)

    def forward(self, draft_terms: str):
        return self.check(
            draft_terms=draft_terms,
            compliance_rules=COMPLIANCE_RULES,
        )
