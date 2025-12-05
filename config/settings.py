# config/settings.py (更新版本)

import dspy
import os
import pandas as pd
# from pymilvus import connections, utility # 实际 Milvus 库
from dotenv import load_dotenv

load_dotenv()

# --- 1. 模拟 Milvus 检索器 ---
class MilvusRetriever(dspy.Retrieve):
    """
    Self-host Milvus-based retriever for structured and unstructured procurement data.
    Used for Contracts, Audits, and Suppliers retrieval.
    """
    def __init__(self, k: int = 3, collection_name: str = "contracts"):
        super().__init__(k=k)
        self.collection_name = collection_name
        # 实际代码中：connections.connect(alias="default", host="...", port="...")
        
        # 模拟加载 Suppliers CSV 作为辅助数据
        try:
            self.suppliers_df = pd.read_csv("mock_data/suppliers.csv")
        except FileNotFoundError:
            self.suppliers_df = None
            print("⚠️ suppliers.csv not found. RAG will be limited.")

    def forward(self, query_or_supplier_id: str, k: int = None) -> dspy.Prediction:
        k = k if k is not None else self.k
        
        # --- 抽象检索逻辑 ---
        if self.collection_name == "suppliers":
            # 检索结构化数据：查找特定的供应商信息
            if self.suppliers_df is not None:
                # 假设 query_or_supplier_id 是 supplier_id
                supplier_info = self.suppliers_df[
                    self.suppliers_df['supplier_id'].str.contains(query_or_supplier_id, case=False)
                ].to_dict('records')
                
                context = [f"Supplier Info: {info}" for info in supplier_info]
                
            else:
                context = ["Placeholder: Supplier database is unavailable."]

        else: 
            # 检索非结构化文档 (Contracts/Audits)
            # 实际代码中：results = milvus_client.search(collection_name, query_vector, k)
            # 模拟检索：基于关键词和 collection_name 返回相关的 mock 文档片段
            if self.collection_name == "contracts":
                context = [
                    f"Contract Snippet: For {query_or_supplier_id}, Payment Term is Net 60 days.",
                    f"Contract Snippet: For {query_or_supplier_id}, Penalty clause is 15% of shipment value.",
                ]
            elif self.collection_name == "audits":
                context = [
                    f"Audit Risk: Found CRITICAL issue in {query_or_supplier_id} related to Forced Labor.",
                    f"Audit History: Last audit date {fake.date_between(start_date='-1y', end_date='today')}."
                ]
            else:
                context = ["Placeholder: No relevant document retrieved."]
                
        # Return the retrieved context as Prediction
        return dspy.Prediction(context=context)


def initialize_dspy_settings(lm_model: str = 'gemini-2.5-flash', k_retrievals: int = 3):
    """
    Initialize DSPy global settings with a specified LLM and custom Milvus retrievers.
    1. LLM Configuration
    2. Milvus Retriever Configuration for Contracts and Audits
    3. Global Settings Application
    """
    api_key = os.getenv("API_KEY_DSPY")
    lm = dspy.LM("openai/gpt-4.1-mini", temperature=0.5, api_key=api_key, max_tokens=32000)

    try:
        contract_retriever = MilvusRetriever(k=k_retrievals, collection_name="contracts")
        audit_retriever = MilvusRetriever(k=k_retrievals, collection_name="audits")
        supplier_retriever = MilvusRetriever(k=1, collection_name="suppliers") 
        
        dspy.settings.configure(lm=lm, rm=contract_retriever)
        print("RM configured: Custom MilvusRetriever (Contracts) set as default.")
        
        return {
            "contract_retriever": contract_retriever,
            "audit_retriever": audit_retriever,
            "supplier_retriever": supplier_retriever
        }

    except Exception:
        raise RuntimeError("Failed to initialize DSPy settings with Milvus retrievers.")