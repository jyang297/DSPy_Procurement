from config.retrievers import MilvusRetriever
from config.settings import configure_dspy
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
    collection="suppliers_demo",
    top_k=3,
)

contract_r = MilvusRetriever(
    uri=MILVUS_URI,
    user=USERNAME,
    password=PASSWORD,
    collection="contracts_demo",
    top_k=3,
)

audit_r = MilvusRetriever(
    uri=MILVUS_URI,
    user=USERNAME,
    password=PASSWORD,
    collection="audits_demo",
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
if __name__ == "__main__":
    raw_request = input("Enter procurement request: ")
    if raw_request.strip() == "":
        raw_request = """
        We need IT servers for our Montreal data center upgrade.
        Expected budget: around 40k-60k.
        Delivery must be within 5 weeks.
        """

    result = agent(raw_request)

    print("\n====== FINAL RESULT ======\n")
    print(result)
