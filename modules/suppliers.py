import dspy


# Signature describing the inputs/outputs needed to rank suppliers against a refined requirement.
class SupplierRankSignature(dspy.Signature):
    # Input fields
    specification: str = dspy.InputField(
        desc="Structured procurement requirements including category, key specs, budget, and delivery date."
    )
    supplier_context: str = dspy.InputField(
        desc=(
            "Retrieved supplier information. MUST include the supplier_id field in the format "
            "'supplier_id: XXX'. The final answer MUST choose one supplier_id that appears here."
        )
    )
    contract_context: str = dspy.InputField(
        desc="Context retrieved from the supplier's contract history or similar contracts."
    )

    # Output fields
    top_supplier_id: str = dspy.OutputField(
        desc=(
            "Return EXACTLY ONE supplier_id string. The value MUST be one that appears in supplier_context. "
            "NEVER answer 'N/A', 'unknown', or make up an ID."
        )
    )
    reasoning: str = dspy.OutputField(
        desc="Explain reasoning based on supplier_context and contract_context."
    )
