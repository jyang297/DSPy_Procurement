# modules/ranking.py
import dspy
from modules.signatures import SupplierRankSignature


# Wraps a DSPy ChainOfThought call so we can swap the ranking prompt without touching the pipeline.
class SupplierRankerModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.rank = dspy.ChainOfThought(SupplierRankSignature)

    def forward(self, specification, supplier_context, contract_context):
        return self.rank(
            specification=specification,
            supplier_context=supplier_context,
            contract_context=contract_context,
        )
