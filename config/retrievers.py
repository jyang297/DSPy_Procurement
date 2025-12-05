# MyMilvus/milvus_retrievers.py
import dspy
from pymilvus import MilvusClient, model
import os 

openai_ef = model.dense.OpenAIEmbeddingFunction(
    model_name="text-embedding-3-small",
    api_key=os.environ["OPENAI_API_KEY"],
)

class MilvusRetriever(dspy.Retrieve):
    def __init__(self, uri, user, password, collection, top_k=3):
        super().__init__(k=top_k)
        self.client = MilvusClient(uri=uri, user=user, password=password)
        self.collection = collection

    def forward(self, query: str, k=None, **kwargs) -> dspy.Prediction:
        k = k or self.k

        # Embed query using OpenAIEmbedding
        query_emb = openai_ef.encode_queries([query])[0]

        # Search Milvus
        hits = self.client.search(
            collection_name=self.collection,
            data=[query_emb],
            limit=k,
            output_fields=["text", "supplier_id"],
        )[0] 

        contexts = []
        for h in hits:
            entity = h["entity"]
            txt = entity.get("text", "")
            contexts.append(txt)

        return dspy.Prediction(context=contexts)
