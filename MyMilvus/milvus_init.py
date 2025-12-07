# milvus_init_all.py
import csv
import os
import sys
from glob import glob
from pathlib import Path
from pymilvus import MilvusClient, model

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from MyMilvus.milvus_collections import load_collection_names

# ----------------------------
# Milvus client init
# ----------------------------
client = MilvusClient(
    uri="http://localhost:19530",
    user="root",
    password="Milvus"
)

# ----------------------------
# Embedding model init
# ----------------------------
openai_ef = model.dense.OpenAIEmbeddingFunction(
    model_name="text-embedding-3-small",
    api_key=os.environ["OPENAI_API_KEY"],
)

collections = load_collection_names()


# -----------------------------------------------------------
# 1) SUPPLIERS COLLECTION (from suppliers.csv)
# -----------------------------------------------------------
SUPPLIER_COLLECTION = collections["suppliers"]

if client.has_collection(SUPPLIER_COLLECTION):
    # Replace any previous demo collection so the run is idempotent.
    client.drop_collection(SUPPLIER_COLLECTION)

client.create_collection(
    collection_name=SUPPLIER_COLLECTION,
    dimension=1536,
    vector_field="vector",
    primary_field="id",
    id_type="int",
    enable_dynamic_field=True,
)

print(f"Created collection: {SUPPLIER_COLLECTION}")


supplier_rows = []

with open("mock_data/suppliers.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    expected_fields = [
        "supplier_id",
        "name",
        "category",
        "region",
        "contact_email",
        "sustainability_score",
        "contract_active",
        "last_audit_date"
    ]

    # Safety check
    if reader.fieldnames != expected_fields:
        raise ValueError(
            f"CSV columns do not match expected structure.\n"
            f"Expected: {expected_fields}\n"
            f"Got:      {reader.fieldnames}"
        )

    for i, row in enumerate(reader):
        supplier_id = row["supplier_id"]

        # Build a structured description for embeddings
        description = (
            f"Supplier {row['name']} (ID {row['supplier_id']}) operates in the {row['category']} domain, "
            f"serving customers in the {row['region']} region. "
            f"Contact email: {row['contact_email']}. "
            f"Sustainability score: {row['sustainability_score']}. "
            f"Contract active: {row['contract_active']}. "
            f"Last audit date: {row['last_audit_date']}."
        )

        # Embed description using Milvus 2.6.4 embedding API
        emb = openai_ef.encode_documents([description])[0]

        supplier_rows.append({
            "id": i,
            "supplier_id": supplier_id,
            "description": description,
            "vector": emb,
        })

client.insert(SUPPLIER_COLLECTION, supplier_rows)

print(f"Inserted {len(supplier_rows)} suppliers\n")


# -----------------------------------------------------------
# 2 CONTRACTS COLLECTION (SUP-XXXX.md)
# -----------------------------------------------------------
CONTRACT_COLLECTION = collections["contracts"]

if client.has_collection(CONTRACT_COLLECTION):
    client.drop_collection(CONTRACT_COLLECTION)

client.create_collection(
    collection_name=CONTRACT_COLLECTION,
    dimension=1536,
    vector_field="vector",
    primary_field="id",
    id_type="int",
    enable_dynamic_field=True,
)

print(f"Created collection: {CONTRACT_COLLECTION}")


contract_rows = []
contract_files = glob("mock_data/contracts/SUP-*.md")

for idx, filepath in enumerate(contract_files):
    supplier_id = os.path.basename(filepath).split(".")[0]  # SUP-1001

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read().strip()

    # embed contract text
    emb = openai_ef.encode_documents([content])[0]

    contract_rows.append({
        "id": idx,
        "supplier_id": supplier_id,
        "text": content,
        "vector": emb,
    })

client.insert(CONTRACT_COLLECTION, contract_rows)

print(f"Inserted {len(contract_rows)} contract docs\n")


# -----------------------------------------------------------
# 3) AUDITS COLLECTION (SUP-XXXX.md)
# -----------------------------------------------------------
AUDIT_COLLECTION = collections["audits"]

if client.has_collection(AUDIT_COLLECTION):
    client.drop_collection(AUDIT_COLLECTION)

client.create_collection(
    collection_name=AUDIT_COLLECTION,
    dimension=1536,
    vector_field="vector",
    primary_field="id",
    id_type="int",
    enable_dynamic_field=True,
)

print(f"Created collection: {AUDIT_COLLECTION}")


audit_rows = []
audit_files = glob("mock_data/audits/SUP-*.md")

for idx, filepath in enumerate(audit_files):
    supplier_id = os.path.basename(filepath).split(".")[0]

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read().strip()

    emb = openai_ef.encode_documents([content])[0]

    audit_rows.append({
        "id": idx,
        "supplier_id": supplier_id,
        "text": content,
        "vector": emb,
    })

client.insert(AUDIT_COLLECTION, audit_rows)

print(f"Inserted {len(audit_rows)} audit docs\n")


print("All data imported successfully.")
