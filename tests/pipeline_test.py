import os
import dspy

from config.settings import configure_dspy  
from config.retrievers import MilvusRetriever
from pipeline import ProcurementWorkflow


# -------------------------------
# 1. Configure DSPy (LM + embedding)
# -------------------------------
configure_dspy()  


# -------------------------------
# 2. Initialize Milvus retrievers
# -------------------------------
MILVUS_URI = "http://localhost:19530"
USERNAME = "root"
PASSWORD = "Milvus"

supplier_r = MilvusRetriever(
    uri=MILVUS_URI,
    user=USERNAME,
    password=PASSWORD,
    collection="suppliers_latest",
    top_k=3,
)

contract_r = MilvusRetriever(
    uri=MILVUS_URI,
    user=USERNAME,
    password=PASSWORD,
    collection="contracts_latest",
    top_k=3,
)

audit_r = MilvusRetriever(
    uri=MILVUS_URI,
    user=USERNAME,
    password=PASSWORD,
    collection="audits_latest",
    top_k=3,
)


# -------------------------------
# 3. Initialize Workflow
# -------------------------------
agent = ProcurementWorkflow(
    supplier_r=supplier_r,
    contract_r=contract_r,
    audit_r=audit_r,
)


# -------------------------------
# 4. Test query
# -------------------------------
raw_request = """
We need IT servers for our Montreal data center upgrade.
Expected budget: around 40k-60k.
Delivery must be within 5 weeks.
"""

result = agent(raw_request)

print("\n====== FINAL RESULT ======\n")
print(result)
