import dspy

class ComplianceChecker(dspy.Signature):
    """
    Examines draft contract terms against company procurement and legal compliance requirements.
    """
    # Input fields
    draft_terms: str = dspy.InputField(desc="Draft contract terms in text format.")
    compliance_rules: str = dspy.InputField(desc="The key procurement and legal compliance rules in text format.") 
    
    # Output fields
    is_compliant: bool = dspy.OutputField(desc="If the draft terms comply with the rules, true; otherwise, false.")
    rejection_reason: str = dspy.OutputField(desc="If not compliant, provide the reason for rejection.")