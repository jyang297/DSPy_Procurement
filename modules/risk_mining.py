# modules/risk_mining.py
import dspy
from modules.signatures import RiskMiningSignature

class RiskMiner(dspy.Module):
    def __init__(self, audit_r, supplier_r):
        super().__init__()
        self.audit_r = audit_r
        self.supplier_r = supplier_r
        self.miner = dspy.ChainOfThought(RiskMiningSignature)

    def forward(self, supplier_id):
        supplier_info = self.supplier_r(supplier_id).context[0]
        audit_info = self.audit_r(supplier_id).context[0]
        return self.miner(
            supplier_id=supplier_id,
            supplier_info=supplier_info,
            audit_context=audit_info,
        )
