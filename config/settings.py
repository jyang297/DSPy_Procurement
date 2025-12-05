# config/settings.py
import dspy
import os
from dotenv import load_dotenv
from retrievers import SupplierRetriever, ContractRetriever, AuditRetriever

load_dotenv()

def configure_dspy(
        lm_model: str = "openai/gpt-4o",
        k: int = 3,
):
    """Configure DSPy with modern LM and custom RM."""


    if "gpt" in lm_model:
        lm = dspy.LM(model=lm_model, api_key=os.getenv("OPENAI_API_KEY"))
    else:
        raise ValueError("Unsupported LM")

    # -------- RM --------
    # DSPy only allows 1 default RM → Assign ContractRetriever as default
    default_rm = ContractRetriever(k=k)

    dspy.settings.configure(lm=lm, rm=default_rm)
    
    # -------- Retrievers --------
    

    # Return the retrievers so pipeline.py can use them
    return {
        "supplier_r": SupplierRetriever(k=k),
        "contract_r": ContractRetriever(k=k),
        "audit_r": AuditRetriever(k=k),
    }
