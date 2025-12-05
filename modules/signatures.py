import dspy

class RequirementSpecSignature(dspy.Signature):
    raw_request: str = dspy.InputField(desc="The unstructured procurement request provided by the user.")
    feedback: str = dspy.InputField(desc="Correction or missing information identified during refinement, or 'none'.")

    item_category: str = dspy.OutputField(desc="High-level category of the requested item (e.g., IT hardware, chemicals).")
    key_specifications: list[str] = dspy.OutputField(desc="List of essential specifications extracted from the raw request.")
    estimated_budget: str = dspy.OutputField(desc="Budget expressed as a value or range (e.g., '10k-20k USD').")
    required_delivery_date: str = dspy.OutputField(desc="Deadline or delivery expectation extracted from the request.")


class SupplierRankSignature(dspy.Signature):
    specification: str = dspy.InputField(desc="Structured requirement specification derived from the user's request.")
    supplier_context: str = dspy.InputField(desc="Relevant supplier profile retrieved from the supplier database.")
    contract_context: str = dspy.InputField(desc="Past or existing contract text associated with this supplier.")

    top_supplier_id: str = dspy.OutputField(desc="The most suitable supplier ID selected based on ranking.")
    reasoning: str = dspy.OutputField(desc="Natural-language reasoning explaining why the supplier was selected.")


class RiskMiningSignature(dspy.Signature):
    supplier_id: str = dspy.InputField(desc="Supplier identifier to analyze.")
    supplier_info: str = dspy.InputField(desc="Supplier profile including capabilities, certifications, and history.")
    audit_context: str = dspy.InputField(desc="Audit logs, compliance reports, or historical risk findings.")

    risk_summary: str = dspy.OutputField(desc="Short description of risk factors related to this supplier.")
    risk_score: int = dspy.OutputField(desc="Integer score from 0–100 representing supplier risk level.")


class ComplianceSignature(dspy.Signature):
    draft_terms: str = dspy.InputField(desc="Proposed contract terms produced automatically by the system.")
    compliance_rules: str = dspy.InputField(desc="Text containing procurement or legal compliance constraints.")

    is_compliant: bool = dspy.OutputField(desc="Whether the contract terms pass all compliance checks.")
    rejection_reason: str = dspy.OutputField(desc="If not compliant, explanation of which rule(s) were violated.")
