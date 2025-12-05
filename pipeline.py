# pipeline.py
import dspy

from modules.refinement import reward_budget_present, reward_compliance_schema
from modules.analysis import RequirementAnalyzer
from modules.ranking import SupplierRankerModule
from modules.risk_mining import RiskMiner
from modules.safeguards import ContractComplianceChecker


class ProcurementWorkflow(dspy.Module):
    def __init__(self, supplier_r, contract_r, audit_r):
        super().__init__()
        # 需求→结构化
        self.analyzer = RequirementAnalyzer()
        # 供应商选择（用 supplier retriever + contract retriever）
        self.ranker = SupplierRankerModule(supplier_r, contract_r)
        # 风险挖掘（用 audit retriever + supplier retriever）
        self.risk_miner = RiskMiner(audit_r, supplier_r)
        # 合规判断（LLM 模块，本身不负责 safeguard）
        self.compliance_checker = ContractComplianceChecker()

    def forward(self, raw_request: str):
        # -------------------------------
        # Step 1: 需求规范 + Refine safeguard（预算必须存在）
        # -------------------------------
        refined_spec = dspy.Refine(
            module=self.analyzer,          # RequirementAnalyzer 模块
            N=4,                           # 最多采样 4 次
            reward_fn=reward_budget_present,
            threshold=0.0,                 # >0 就算“可接受”
        )(
            raw_request=raw_request,
            feedback="none",               # 你的 Signature 里有 feedback 字段
        )

        spec_json = refined_spec.dump()

        # -------------------------------
        # Step 2: 供应商排序 / 选择
        # -------------------------------
        ranked = self.ranker(spec_json)
        supplier_id = ranked.top_supplier_id

        # -------------------------------
        # Step 3: 风险挖掘
        # -------------------------------
        risk = self.risk_miner(supplier_id)

        # -------------------------------
        # Step 4: 合同草案 + 合规检查（再用 Refine 做 safeguard）
        # -------------------------------
        draft_terms = (
            f"Supplier: {supplier_id}\n"
            f"Budget: {refined_spec.estimated_budget}\n"
            f"Risk summary: {risk.risk_summary}\n"
        )

        refined_compliance = dspy.Refine(
            module=self.compliance_checker,   # ContractComplianceChecker 模块
            N=4,
            reward_fn=reward_compliance_schema,
            threshold=0.0,
        )(
            draft_terms=draft_terms,
        )

        # -------------------------------
        # Step 5: 最终决策输出
        # -------------------------------
        if not refined_compliance.is_compliant:
            return {
                "status": "REQUIRES_REVIEW",
                "supplier": supplier_id,
                "reason": refined_compliance.rejection_reason,
                "risk_score": risk.risk_score,
                "risk_summary": risk.risk_summary,
            }

        return {
            "status": "APPROVED",
            "supplier": supplier_id,
            "specification": spec_json,
            "risk_summary": risk.risk_summary,
        }
