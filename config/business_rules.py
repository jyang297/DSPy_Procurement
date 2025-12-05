# config/business_rules.py
# Target:
# 1. Simple business rules and compliance guidelines for procurement contracts.
# 2. Mock supplier database for testing RAG capabilities.

SUPPLIER_DATABASE_MOCK = (
    "Supplier A: Provides IT hardware, specializes in servers, budget: 10k-50k. Delivery: 4 weeks. "
    "Supplier B: Marketing services, specializes in digital campaigns, budget: 5k-20k. Delivery: 2 weeks. "
    "Supplier C: Raw materials for manufacturing, specializes in polymer X, budget: 50k-100k. Delivery: 6 weeks."
)

COMPLIANCE_RULES = (
    "1. All contracts over $50,000 must include a mandatory 90-day payment term. "
    "2. IT hardware procurement must use suppliers with ISO 27001 certification. "
    "3. No contract should exceed the stated budget by more than 10% without executive approval."
)

REQUIRED_SPEC_KEYS = ['item_category', 'key_specifications', 'estimated_budget']