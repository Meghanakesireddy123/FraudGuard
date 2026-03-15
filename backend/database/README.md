# Database Setup

This folder contains MongoDB database setup and configuration files for FraudGuard.

## Files

- `setup_mongodb.py` - Script to populate MongoDB with sample transactions
- `db_details.txt` - Complete database documentation and connection details
- `extract_fraud_examples.py` - Extract fraud transactions from datasets (Python script)
- `fraud_test_examples.txt` - Pre-made fraud transaction examples for manual testing

## Quick Start

1. **Install dependencies** (if not already installed):
   ```bash
   py -m pip install pymongo pandas
   ```

2. **Run setup script**:
   ```bash
   cd backend/database
   py setup_mongodb.py
   ```

3. **Extract fraud examples** (optional):
   ```bash
   py extract_fraud_examples.py
   ```

4. **Verify** connection details in `db_details.txt`

## Database Information

- **Database:** fraudguard
- **Collections:** card_transactions, upi_transactions
- **Total Transactions:** 200 (150 CARD + 50 UPI)
- **Fraud Rate:** ~32% mixed

## Fraud Test Examples

Use `fraud_test_examples.txt` for manual transaction testing in the dashboard. Contains 15 pre-made examples (10 fraud, 5 legit) with all necessary fields.

See `db_details.txt` for complete connection information and usage examples.
