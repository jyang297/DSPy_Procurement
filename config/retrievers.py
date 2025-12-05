# config/retrievers.py
import dspy
import pandas as pd
import os
import random

import dspy
import pandas as pd

class SupplierRetriever(dspy.Retrieve):
    """Retrieve supplier info from suppliers.csv."""

    def __init__(self, k=1):
        super().__init__(k=k)
        self.df = pd.read_csv("mock_data/suppliers.csv")

    def forward(self, query: str, k: int | None = None, **kwargs) -> dspy.Prediction:
        """query = user text, but we try to match supplier_id."""
        search_key = query.split()[0].lower()

        matches = self.df[self.df["supplier_id"].str.lower().str.contains(search_key)]

        if matches.empty:
            return dspy.Prediction(context=["[NO SUPPLIER FOUND]"])

        row = matches.iloc[0].to_dict()
        return dspy.Prediction(context=[str(row)])



class ContractRetriever(dspy.Retrieve):
    def forward(self, query: str, k: int | None = None, **kwargs) -> dspy.Prediction:
        supplier_id = query.strip()
        # I hardcode contract file path for simplicity
        path = f"mock_data/contracts/{supplier_id}_contract.md"
        if not os.path.exists(path):
            return dspy.Prediction(context=["[NO CONTRACT FOUND]"])
        return dspy.Prediction(context=[open(path).read()])



class AuditRetriever(dspy.Retrieve):
    def forward(self, query: str, k: int | None = None, **kwargs) -> dspy.Prediction:
        supplier_id = query.strip()
        # I hardcode audit file path for simplicity
        path = f"mock_data/audits/{supplier_id}_audit.md"
        if not os.path.exists(path):
            return dspy.Prediction(context=["[NO AUDIT FOUND]"])
        return dspy.Prediction(context=[open(path).read()])

