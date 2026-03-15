# Quick Start Guide - Training Ensemble Models

## Prerequisites
Ensure you have installed all dependencies:
```bash
cd backend
pip install -r requirements.txt
```

## Training the Ensemble Model

### Step 1: Navigate to models directory
```bash
cd models
```

### Step 2: Run the training script
```bash
python train_model.py
```

### What to Expect

The training script will:
1. ✅ Load CARD fraud datasets (fraudTrain.csv, fraudTest.csv)
2. 🔧 Perform feature engineering (time features, amount features, etc.)
3. 🤖 Train 3 base models:
   - Random Forest
   - XGBoost  
   - LightGBM
4. 🗳️ Create voting ensemble combining all 3 models
5. 📊 Evaluate and compare all models
6. 💾 Save the best model as `fraud_detection_system.pkl`

### Training Output

You'll see detailed output like:
```
🚀🚀🚀🚀...
ENSEMBLE FRAUD DETECTION MODEL TRAINING
🚀🚀🚀🚀...

💳 CARD FRAUD DETECTION MODEL TRAINING
================================================================================

📊 Loading CARD datasets...
  Train shape: (1296675, 23)
  Test shape: (555719, 23)
  Sampling 100000 rows for faster training...

🔧 Engineering features for CARD data...
📋 Selected 15 features

📊 Dataset sizes:
  Train: (80000, 15)
  Test: (111144, 15)

================================================================================
🚀 TRAINING ALL MODELS
================================================================================

🎯 Training random_forest...
  ✅ Training complete
  📊 Evaluating random_forest...
    Accuracy: 0.9987
    F1 Score: 0.8542
    ROC AUC: 0.9456
    PR AUC: 0.7234

🎯 Training xgboost...
  ✅ Training complete
  📊 Evaluating xgboost...
    Accuracy: 0.9989
    F1 Score: 0.8756
    ROC AUC: 0.9587
    PR AUC: 0.7654

🎯 Training lightgbm...
  ✅ Training complete
  📊 Evaluating lightgbm...
    Accuracy: 0.9988
    F1 Score: 0.8623
    ROC AUC: 0.9523
    PR AUC: 0.7445

🗳️ Creating voting ensemble...
🎯 Training ensemble...
  ✅ Training complete
  📊 Evaluating ensemble...
    Accuracy: 0.9990
    F1 Score: 0.8842
    ROC AUC: 0.9612
    PR AUC: 0.7789

================================================================================
📈 MODEL PERFORMANCE SUMMARY
================================================================================
                accuracy  f1_score  roc_auc   pr_auc
ensemble         0.9990    0.8842   0.9612   0.7789
xgboost          0.9989    0.8756   0.9587   0.7654
lightgbm         0.9988    0.8623   0.9523   0.7445
random_forest    0.9987    0.8542   0.9456   0.7234

🏆 Best Model: ensemble
   ROC AUC: 0.9612

💾 SAVING MODELS
================================================================================
✅ Saved ensemble model to: ../models/fraud_detection_system.pkl
✅ Saved metadata to: ../models/model_metadata.json

🎉 All models saved successfully!
```

### Configuration Options

You can modify training parameters in `train_model.py`:

```python
class Config:
    # Sampling (for faster training)
    USE_SAMPLING = True  # Set to False for full dataset
    SAMPLE_SIZE = 100000  # Adjust based on your compute power
    
    # Cross-validation
    CV_FOLDS = 5
    
    # Random seed
    RANDOM_STATE = 42
```

## After Training

Once training is complete:

1. The **ensemble model** will be saved at `models/fraud_detection_system.pkl`
2. The **backend** will automatically detect and load this model
3. Start the backend to use ML predictions:
   ```bash
   cd ../backend
   python main.py
   ```

4. You'll see:
   ```
   🚀 Starting Anti-Gravity Fraud Detection System
   ✅ Successfully loaded ensemble model from ../models/fraud_detection_system.pkl
   📋 Model uses 15 features
   📊 Model Status: ML Model Loaded
   ```

## Troubleshooting

### Out of Memory
If you run out of memory:
- Set `USE_SAMPLING = True` and reduce `SAMPLE_SIZE`
- Reduce `n_estimators` in model definitions

### Training Takes Too Long
- Reduce `SAMPLE_SIZE` to 50000 or less
- Reduce `n_estimators` to 50
- Set `n_jobs=-1` to use all CPU cores (already default)

### Python Not Found
- Ensure Python is installed and in PATH
- Try: `python3 train_model.py` or `py train_model.py`

## Model Files

After successful training, you'll have:
- `fraud_detection_system.pkl` - Main ensemble model (used by backend)
- `model_metadata.json` - Training metrics and metadata
