# modules/ranking.py
import dspy
from modules.signatures import SupplierRankSignature

class SupplierRankerModule(dspy.Module):
    def __init__(self, supplier_r, contract_r):
        super().__init__()
        self.supplier_r = supplier_r
        self.contract_r = contract_r
        self.rank = dspy.ChainOfThought(SupplierRankSignature)

    def forward(self, specification: str):
        # retrieve candidates
        supplier_ctx = self.supplier_r(specification).context[0]
        supplier_id = eval(supplier_ctx)["supplier_id"]

        contract_ctx = self.contract_r(supplier_id).context[0]

        return self.rank(
            specification=specification,
            supplier_context=supplier_ctx,
            contract_context=contract_ctx,
        )
