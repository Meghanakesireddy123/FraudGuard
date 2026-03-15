"""
MongoDB Database Setup for FraudGuard
Connects to MongoDB Atlas, creates collections, and populates with sample transactions
"""

import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import random
import json
from urllib.parse import quote_plus

# MongoDB Connection - URL encode password to handle special characters
username = "fraudGuardAdmin"
password = "Admin@123"
cluster = "cluster0.kj6yvox.mongodb.net"

MONGODB_URI = f"mongodb+srv://fraudGuardAdmin:Admin@123@cluster0.kj6yvox.mongodb.net/"
DATABASE_NAME = "fraudguard"

# Collections
CARD_TRANSACTIONS_COLLECTION = "card_transactions"
UPI_TRANSACTIONS_COLLECTION = "upi_transactions"

def connect_to_mongodb():
    """Connect to MongoDB Atlas"""
    try:
        client = MongoClient(MONGODB_URI)
        # Test connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB!")
        return client
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        return None

def get_card_schema():
    """Define CARD transaction schema based on fraudTrain.csv"""
    return {
        "trans_date_trans_time": "datetime",
        "cc_num": "string",
        "merchant": "string",
        "category": "string",
        "amt": "float",
        "first": "string",
        "last": "string",
        "gender": "string",
        "street": "string",
        "city": "string",
        "state": "string",
        "zip": "int",
        "lat": "float",
        "long": "float",
        "city_pop": "int",
        "job": "string",
        "dob": "string",
        "trans_num": "string",
        "unix_time": "int",
        "merch_lat": "float",
        "merch_long": "float",
        "is_fraud": "int"
    }

def get_upi_schema():
    """Define UPI transaction schema based on upi_fraud_dataset.csv"""
    return {
        "Id": "int",
        "trans_hour": "int",
        "trans_day": "int",
        "trans_month": "int",
        "trans_year": "int",
        "upi_number": "string",
        "amount": "float",
        "state": "string",
        "zip": "int",
        "city_pop": "int",
        "fraud_risk": "int"  # Actual column name
    }

def load_and_sample_card_data(sample_size=150):
    """Load and sample CARD transactions"""
    print(f"\n📊 Loading CARD dataset...")
    
    # Read CSV with correct path (from backend/database/)
    df = pd.read_csv("../../datasets/card/fraudTrain.csv")
    print(f"   Total CARD transactions: {len(df)}")
    
    # Sample fraud and legit transactions
    fraud_df = df[df['is_fraud'] == 1].sample(n=min(50, len(df[df['is_fraud'] == 1])), random_state=42)
    legit_df = df[df['is_fraud'] == 0].sample(n=min(100, len(df[df['is_fraud'] == 0])), random_state=42)
    
    # Combine
    sample_df = pd.concat([fraud_df, legit_df]).sample(frac=1, random_state=42)  # Shuffle
    
    print(f"   Sampled: {len(sample_df)} transactions ({len(fraud_df)} fraud, {len(legit_df)} legit)")
    
    # Convert to list of dicts
    return sample_df.to_dict('records')

def load_and_sample_upi_data(sample_size=50):
    """Load and sample UPI transactions"""
    print(f"\n📊 Loading UPI dataset...")
    
    # Read CSV with correct path (from backend/database/)
    df = pd.read_csv("../../datasets/upi/upi_fraud_dataset.csv")
    print(f"   Total UPI transactions: {len(df)}")
    
    # Sample fraud and legit transactions (correct column name)
    fraud_df = df[df['fraud_risk'] == 1].sample(n=min(15, len(df[df['fraud_risk'] == 1])), random_state=42)
    legit_df = df[df['fraud_risk'] == 0].sample(n=min(35, len(df[df['fraud_risk'] == 0])), random_state=42)
    
    # Combine
    sample_df = pd.concat([fraud_df, legit_df]).sample(frac=1, random_state=42)  # Shuffle
    
    print(f"   Sampled: {len(sample_df)} transactions ({len(fraud_df)} fraud, {len(legit_df)} legit)")
    
    # Convert to list of dicts
    return sample_df.to_dict('records')

def insert_card_transactions(db, transactions):
    """Insert CARD transactions into MongoDB"""
    collection = db[CARD_TRANSACTIONS_COLLECTION]
    
    # Clear existing data
    collection.delete_many({})
    
    # Insert new data
    result = collection.insert_many(transactions)
    
    print(f"✅ Inserted {len(result.inserted_ids)} CARD transactions")
    return len(result.inserted_ids)

def insert_upi_transactions(db, transactions):
    """Insert UPI transactions into MongoDB"""
    collection = db[UPI_TRANSACTIONS_COLLECTION]
    
    # Clear existing data
    collection.delete_many({})
    
    # Insert new data
    result = collection.insert_many(transactions)
    
    print(f"✅ Inserted {len(result.inserted_ids)} UPI transactions")
    return len(result.inserted_ids)

def create_indexes(db):
    """Create indexes for better query performance"""
    print("\n📑 Creating indexes...")
    
    # CARD indexes
    card_collection = db[CARD_TRANSACTIONS_COLLECTION]
    card_collection.create_index("trans_num")
    card_collection.create_index("is_fraud")
    card_collection.create_index("merchant")
    
    # UPI indexes
    upi_collection = db[UPI_TRANSACTIONS_COLLECTION]
    upi_collection.create_index("Id")
    upi_collection.create_index("fraud_risk")  # Correct column name
    
    print("✅ Indexes created")

def get_statistics(db):
    """Get database statistics"""
    stats = {
        "database": DATABASE_NAME,
        "collections": {}
    }
    
    # CARD stats
    card_col = db[CARD_TRANSACTIONS_COLLECTION]
    card_total = card_col.count_documents({})
    card_fraud = card_col.count_documents({"is_fraud": 1})
    
    stats["collections"][CARD_TRANSACTIONS_COLLECTION] = {
        "total": card_total,
        "fraud": card_fraud,
        "legit": card_total - card_fraud,
        "fraud_rate": f"{(card_fraud/card_total*100):.2f}%" if card_total > 0 else "0%"
    }
    
    # UPI stats
    upi_col = db[UPI_TRANSACTIONS_COLLECTION]
    upi_total = upi_col.count_documents({})
    upi_fraud = upi_col.count_documents({"fraud_risk": 1})  # Correct column name
    
    stats["collections"][UPI_TRANSACTIONS_COLLECTION] = {
        "total": upi_total,
        "fraud": upi_fraud,
        "legit": upi_total - upi_fraud,
        "fraud_rate": f"{(upi_fraud/upi_total*100):.2f}%" if upi_total > 0 else "0%"
    }
    
    return stats

def save_db_details(stats):
    """Save database connection details and statistics"""
    details = f"""# FraudGuard MongoDB Database Details

## Connection Information
- **URI:** {MONGODB_URI}
- **Database:** {DATABASE_NAME}
- **Connection Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Collections

### {CARD_TRANSACTIONS_COLLECTION}
- **Total Transactions:** {stats['collections'][CARD_TRANSACTIONS_COLLECTION]['total']}
- **Fraud Transactions:** {stats['collections'][CARD_TRANSACTIONS_COLLECTION]['fraud']}
- **Legitimate Transactions:** {stats['collections'][CARD_TRANSACTIONS_COLLECTION]['legit']}
- **Fraud Rate:** {stats['collections'][CARD_TRANSACTIONS_COLLECTION]['fraud_rate']}

**Schema Fields (23 fields):**
```
trans_date_trans_time, cc_num, merchant, category, amt, first, last, 
gender, street, city, state, zip, lat, long, city_pop, job, dob, 
trans_num, unix_time, merch_lat, merch_long, is_fraud
```

### {UPI_TRANSACTIONS_COLLECTION}
- **Total Transactions:** {stats['collections'][UPI_TRANSACTIONS_COLLECTION]['total']}
- **Fraud Transactions:** {stats['collections'][UPI_TRANSACTIONS_COLLECTION]['fraud']}
- **Legitimate Transactions:** {stats['collections'][UPI_TRANSACTIONS_COLLECTION]['legit']}
- **Fraud Rate:** {stats['collections'][UPI_TRANSACTIONS_COLLECTION]['fraud_rate']}

**Schema Fields (11 fields):**
```
Id, trans_hour, trans_day, trans_month, trans_year, upi_number, 
amount, state, zip, city_pop, fraud_risk
```

## Indexes Created
- CARD: trans_num, is_fraud, merchant
- UPI: Id, fraud_risk

## Usage Examples

### Python (PyMongo)
```python
from pymongo import MongoClient

client = MongoClient("{MONGODB_URI}")
db = client["{DATABASE_NAME}"]

# Get all fraud transactions
fraud_txns = db.{CARD_TRANSACTIONS_COLLECTION}.find({{"is_fraud": 1}})

# Count legitimate UPI transactions
legit_count = db.{UPI_TRANSACTIONS_COLLECTION}.count_documents({{"fraud_risk": 0}})
```

### MongoDB Compass
1. Open MongoDB Compass
2. Connect using URI: `{MONGODB_URI}`
3. Navigate to database: `{DATABASE_NAME}`
4. Browse collections

## Notes
- Data sourced from CARD (fraudTrain.csv) and UPI (upi_fraud_dataset.csv) datasets
- Sample data includes mix of fraud and legitimate transactions
- Passwords and sensitive info should be rotated in production
"""
    
    with open("db_details.txt", "w") as f:
        f.write(details)
    
    print("\n✅ Database details saved to db_details.txt")

def main():
    """Main execution"""
    print("=" * 80)
    print("🚀 FraudGuard MongoDB Database Setup")
    print("=" * 80)
    
    # Connect to MongoDB
    client = connect_to_mongodb()
    if not client:
        print("❌ Failed to connect to MongoDB. Exiting.")
        return
    
    # Get database
    db = client[DATABASE_NAME]
    print(f"\n📦 Using database: {DATABASE_NAME}")
    
    # Load and insert CARD transactions
    card_transactions = load_and_sample_card_data(150)
    insert_card_transactions(db, card_transactions)
    
    # Load and insert UPI transactions
    upi_transactions = load_and_sample_upi_data(50)
    insert_upi_transactions(db, upi_transactions)
    
    # Create indexes
    create_indexes(db)
    
    # Get statistics
    stats = get_statistics(db)
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 DATABASE SUMMARY")
    print("=" * 80)
    print(json.dumps(stats, indent=2))
    
    # Save details to file
    save_db_details(stats)
    
    print("\n" + "=" * 80)
    print("✅ MongoDB setup complete!")
    print("=" * 80)
    
    # Close connection
    client.close()

if __name__ == "__main__":
    main()
