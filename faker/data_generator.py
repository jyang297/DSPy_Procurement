import os
import random

import pandas as pd

from faker import Faker

# Initialization
fake = Faker()
Faker.seed(42)
output_dir = "mock_data"
# Ensure deterministic directories exist for contracts and audits.
os.makedirs(f"{output_dir}/contracts", exist_ok=True)
os.makedirs(f"{output_dir}/audits", exist_ok=True)

# Domain Setup
CATEGORIES = ["Palm Oil", "Fragrance", "rPET Packaging", "Industrial Chemicals"]
REGIONS = ["Indonesia", "Malaysia", "Vietnam", "Brazil", "Netherlands"]
RISK_LEVELS = ["Low", "Medium", "High"]


def generate_suppliers(n=10):
    # Generate the suppliers' information
    data = []
    for i in range(n):
        supplier_id = f"SUP-{1000+i}"
        category = random.choice(CATEGORIES)
        region = random.choice(REGIONS)

        # Risk generation
        base_score = random.randint(60, 95)
        if region in ["Indonesia", "Vietnam"] and category == "Palm Oil":
            base_score -= random.randint(0, 15)

        supplier = {
            "supplier_id": supplier_id,
            "name": f"{fake.company()} {category} Ltd",
            "category": category,
            "region": region,
            "contact_email": fake.company_email(),
            "sustainability_score": max(0, min(100, base_score)),  # 0-100
            "contract_active": random.choice([True, True, False]),
            "last_audit_date": fake.date_between(start_date="-2y", end_date="today"),
        }
        data.append(supplier)

    df = pd.DataFrame(data)
    csv_path = f"{output_dir}/suppliers.csv"
    df.to_csv(csv_path, index=False)
    print(f"Generated {n} suppliers in {csv_path}")
    return df


def generate_contract_text(supplier):
    # Generate unstructured contract
    payment_terms = random.choice(["Net 30", "Net 60", "Net 90"])
    penalty = random.randint(5, 20)

    content = f"""# Master Services Agreement (MSA)
**Supplier:** {supplier['name']} ({supplier['supplier_id']})
**Date:** {fake.date_between(start_date='-3y', end_date='-1y')}
**Category:** {supplier['category']}

## 1. Scope of Supply
The Supplier agrees to provide {supplier['category']} in accordance with Unilever's quality standards (UL-STD-2024).

## 2. Pricing and Payment Terms
* **Base Currency:** USD
* **Payment Terms:** {payment_terms} days from receipt of valid invoice.
* **Price Adjustments:** Prices are fixed for 12 months. Any increase requires 60 days' notice.

## 3. Compliance & Sustainability
The Supplier warrants compliance with the Responsible Sourcing Policy (RSP).
* **Carbon Footprint:** Must report Scope 1 & 2 emissions quarterly.
* **Penalty:** Failure to meet delivery schedules will incur a penalty of {penalty}% of the shipment value.

## 4. Termination
This agreement may be terminated by either party with 90 days written notice.
"""
    return content


def generate_audit_report(supplier):
    # Report with risk (Markdown)

    # 30% for risk
    has_issue = supplier["sustainability_score"] < 70
    # Reuse a small set of audit findings so RAG pipelines have predictable patterns to learn from.

    risk_text = "No critical non-compliances were observed during the site visit."
    if has_issue:
        # RAG is supposed to work on this
        issues = [
            "**CRITICAL:** Evidence of excessive overtime working hours (80+ hours/week) was found in the packaging unit.",
            "**MAJOR:** Waste water treatment plant was bypassed during heavy rains, leading to direct discharge into local river.",
            "**CRITICAL:** Several workers were unable to access their passports, which were held by management (Indicator of Forced Labor).",
            "**MAJOR:** The fire suppression system in the warehouse is non-functional and certification has expired.",
        ]
        risk_text = random.choice(issues)

    content = f"""# Supplier Social & Environmental Audit Report
**Target Entity:** {supplier['name']}
**Location:** {supplier['region']}
**Audit Date:** {supplier['last_audit_date']}
**Auditor:** Intertek / SGS (Simulated)

## Executive Summary
This audit was conducted against the Unilever Sustainable Living Plan standards.

## Section A: Labor Standards
* Child Labor: None observed.
* Wages: Minimum wage standards met.
* **Working Hours & Conditions:** {risk_text if "overtime" in risk_text or "passports" in risk_text else "Compliant with local laws."}

## Section B: Health, Safety & Environment (HSE)
* PPE Usage: 95% compliance.
* **Environmental Impact:** {risk_text if "Water" in risk_text or "fire" in risk_text else "Waste management logs are up to date."}

## Conclusion
    The supplier is graded as: {'**At Risk**' if has_issue else 'Satisfactory'}.
"""
    return content


def main():
    print("Starting data generation for Unilever demo...")

    # 1. Generate Supplier
    suppliers_df = generate_suppliers(20)

    # 2. Generate Unstructured Docs
    for _, row in suppliers_df.iterrows():
        # Generate contracts
        contract_md = generate_contract_text(row)
        with open(f"{output_dir}/contracts/{row['supplier_id']}_contract.md", "w") as f:
            f.write(contract_md)

        # Generate Auidt
        audit_md = generate_audit_report(row)
        with open(f"{output_dir}/audits/{row['supplier_id']}_audit.md", "w") as f:
            f.write(audit_md)

    print(f"Generated 20 contracts and 20 audit reports in '{output_dir}/'")
    print("Done! You can now ingest this into Milvus.")


if __name__ == "__main__":
    main()
