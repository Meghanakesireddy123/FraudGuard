"""
Extract fraud transactions from datasets for manual testing
"""

import pandas as pd
import json

print("=" * 80)
print("FRAUD TRANSACTIONS FOR MANUAL TESTING")
print("=" * 80)

# Load CARD fraud transactions
print("\n📊 Loading CARD dataset...")
card_df = pd.read_csv("../../datasets/card/fraudTrain.csv")
card_fraud = card_df[card_df['is_fraud'] == 1].head(10)

print(f"\n🚨 CARD FRAUD TRANSACTIONS (10 samples):\n")
print("-" * 80)

for idx, row in card_fraud.iterrows():
    print(f"\n#{idx + 1}:")
    print(f"  Type: CARD")
    print(f"  Amount: ₹{row['amt']:.2f}")
    print(f"  Merchant: {row['merchant']}")
    print(f"  Category: {row['category']}")
    print(f"  Location: {row['city']}, {row['state']}")
    print(f"  Time: {row['trans_date_trans_time']}")
    print(f"  ⚠️ FRAUD: Yes")
    print("-" * 80)

# Load UPI fraud transactions
print("\n\n📊 Loading UPI dataset...")
upi_df = pd.read_csv("../../datasets/upi/upi_fraud_dataset.csv")
upi_fraud = upi_df[upi_df['fraud_risk'] == 1].head(5)

print(f"\n🚨 UPI FRAUD TRANSACTIONS (5 samples):\n")
print("-" * 80)

for idx, row in upi_fraud.iterrows():
    print(f"\n#{idx + 1}:")
    print(f"  Type: UPI")
    print(f"  Amount: ₹{row['amount']:.2f}")
    print(f"  State: {row['state']}")
    print(f"  Time: {row['trans_hour']}:00 on {row['trans_month']}/{row['trans_day']}/{row['trans_year']}")
    print(f"  ⚠️ FRAUD: Yes")
    print("-" * 80)

# Save to JSON for easy access
fraud_examples = {
    "card_fraud": [],
    "upi_fraud": []
}

for idx, row in card_fraud.iterrows():
    fraud_examples["card_fraud"].append({
        "type": "CARD",
        "amount": float(row['amt']),
        "merchant": row['merchant'],
        "category": row['category'],
        "location": f"{row['city']}, {row['state']}"
    })

for idx, row in upi_fraud.iterrows():
    fraud_examples["upi_fraud"].append({
        "type": "UPI",
        "amount": float(row['amount']),
        "state": row['state'],
        "hour": int(row['trans_hour'])
    })

# Save to file
with open("fraud_transactions_examples.json", "w") as f:
    json.dump(fraud_examples, f, indent=2)

print("\n\n✅ Saved fraud examples to: fraud_transactions_examples.json")
print("=" * 80)
