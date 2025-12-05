import dspy

class SupplierRanker(dspy.Signature):
    """
    Ranking and selecting the most suitable suppliers based on structured requirement specifications and retrieved supplier data.
    """
    # Input fields
    specification: str = dspy.InputField(desc="Structured requirement specification in JSON format.")
    retrieved_suppliers: str = dspy.InputField(desc="List of retrieved suppliers in JSON format.")
    
    # Output fields
    top_ranked_suppliers: list[dict] = dspy.OutputField(
        desc=" Top ranked suppliers with details including 'supplier_id', 'rank', 'matching_score' 和 'reasoning'。",
    )
    