# modules/risk_mining.py
import dspy

from modules.signatures import RiskMiningSignature


class RiskMiner(dspy.Module):
    def __init__(self):
        super().__init__()
        self.miner = dspy.ChainOfThought(RiskMiningSignature)

    def forward(self, supplier_id, supplier_info, audit_context):
        return self.miner(
            supplier_id=supplier_id,
            supplier_info=supplier_info,
            audit_context=audit_context,
        )
