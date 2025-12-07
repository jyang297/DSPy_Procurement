# config/settings.py
import dspy
import os
from dotenv import load_dotenv
from config.retrievers import MilvusRetriever
from MyMilvus.milvus_collections import load_collection_names

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
    default_rm = None # we have set up retrievers for following different scenarios

    dspy.settings.configure(lm=lm, rm=default_rm)

    # -------- Retrievers --------
    collections = load_collection_names()
    supplier_r = MilvusRetriever(
        uri="http://localhost:19530",
        user="root",
        password="Milvus",
        collection=collections["suppliers"],
        top_k=3,
    )

    contract_r = MilvusRetriever(
        uri="http://localhost:19530",
        user="root",
        password="Milvus",
        collection=collections["contracts"],
        top_k=3,
    )

    audit_r = MilvusRetriever(
        uri="http://localhost:19530",
        user="root",
        password="Milvus",
        collection=collections["audits"],
        top_k=3,
    )

    # Return the retrievers so pipeline.py can use them
    return supplier_r, contract_r, audit_r
