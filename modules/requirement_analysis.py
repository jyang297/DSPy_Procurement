import dspy

class RequirementSpecification(dspy.Signature):
    """
    Converting unstructured procurement requests into structured requirement specifications.    
    """
    # Input fields
    raw_request: str = dspy.InputField(desc="Original unstructured procurement request text.")
    
    # Output fields
    item_category: str = dspy.OutputField(desc="The category of the item or service being procured.")
    key_specifications: list[str] = dspy.OutputField(desc="The key specifications or features required.")
    estimated_budget: str = dspy.OutputField(desc="The estimated budget for the procurement.")
    required_delivery_date: str = dspy.OutputField(desc="The required delivery date for the item or service.")
