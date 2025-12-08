# pipeline.py
import dspy

from config.business_rules import COMPLIANCE_RULES
from modules.analysis import RequirementAnalyzer
from modules.ranking import SupplierRankerModule
from modules.refinement import reward_budget_present, reward_compliance_schema
from modules.risk_mining import RiskMiner
from modules.safeguards import ContractComplianceChecker


# Orchestrates supplier selection, contract checks, and compliance refinement in one DSPy workflow.
class ProcurementWorkflow(dspy.Module):
    def __init__(self, supplier_r, contract_r, audit_r):
        super().__init__()
        self.supplier_r = supplier_r
        self.contract_r = contract_r
        self.audit_r = audit_r
        self.analyzer = RequirementAnalyzer()
        self.ranker = SupplierRankerModule()
        self.risk_miner = RiskMiner()
        self.compliance = ContractComplianceChecker()

    def forward(self, raw_request: str):
        """
        Complete procurement workflow:
        1) Requirement refinement
        2) Supplier RAG
        3) Contract RAG
        4) Supplier Ranking
        5) Audit RAG + Risk Mining
        6) Compliance refinement
        7) Final approval decision
        """

        # ------------------------------------------------------
        # Step 1 — Refine Requirement Specification
        # ------------------------------------------------------
        # We run 4 candidates and choose best one based on reward_budget_present
        refined_spec = dspy.Refine(
            module=self.analyzer,
            N=4,
            reward_fn=reward_budget_present,
            threshold=0.0,
        )(raw_request=raw_request, feedback="none")

        spec = refined_spec  # Prediction object
        # Convert the DSPy prediction to a JSON-serializable dict so downstream modules can access fields.
        spec_json = spec.toDict()

        # ------------------------------------------------------
        # Step 2 — Supplier RAG
        # Query Milvus using structured requirement fields
        # ------------------------------------------------------
        rag_query = f"{spec.item_category} {spec.key_specifications} {spec.estimated_budget}"
        print("----------------------------------")
        print("RAG Query:", rag_query)
        print("----------------------------------")
        supplier_ctx_list = self.supplier_r(rag_query).context
        # Merge multiple supplier hits into a single prompt-friendly blob.
        supplier_ctx = "\n".join(supplier_ctx_list)

        # ------------------------------------------------------
        # Step 3 — Contract RAG
        # Contract context is REQUIRED by SupplierRankSignature
        # So contract RAG must come BEFORE ranking
        # ------------------------------------------------------
        contract_ctx_list = self.contract_r(rag_query).context
        # Keep the contract context as a multiline string so ranking and compliance can reference clauses.
        contract_ctx = "\n".join(contract_ctx_list)

        # ------------------------------------------------------
        # Step 4 — Ranking
        # SupplierRankSignature requires 3 inputs:
        #   - specification
        #   - supplier_context
        #   - contract_context
        # ------------------------------------------------------
        ranked = self.ranker(
            specification=spec_json,
            supplier_context=supplier_ctx,
            contract_context=contract_ctx,
        )

        supplier_id = ranked.top_supplier_id

        # ------------------------------------------------------
        # Step 5 — Audit RAG + Risk Mining
        # RiskMiningSignature requires:
        #   supplier_id, supplier_info, audit_context
        # ------------------------------------------------------
        supplier_info = self.supplier_r(supplier_id).context[0]
        audit_info = self.audit_r(supplier_id).context[0]

        risk = self.risk_miner(
            supplier_id=supplier_id,
            supplier_info=supplier_info,
            audit_context=audit_info,
        )

        # ------------------------------------------------------
        # Step 6 — Compliance Refinement
        # Use Refine to enforce schema correctness & compliance rules
        # ------------------------------------------------------
        draft_terms = contract_ctx

        compliance = dspy.Refine(
            module=self.compliance,
            N=4,
            reward_fn=reward_compliance_schema,
            threshold=0.0,
        )(
            draft_terms=draft_terms,
            compliance_rules=COMPLIANCE_RULES,
        )

        # ------------------------------------------------------
        # Step 7 — Make decision
        # ------------------------------------------------------
        if not compliance.is_compliant:
            return {
                "status": "REQUIRES_REVIEW",
                "reason": compliance.rejection_reason,
                "supplier": supplier_id,
                "risk_score": risk.risk_score,
            }

        return {
            "status": "APPROVED",
            "supplier": supplier_id,
            "risk_summary": risk.risk_summary,
            "risk_score": risk.risk_score,
        }
