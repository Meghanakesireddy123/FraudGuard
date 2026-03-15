"""
Advanced Fraud Detection System with Stacking Ensemble
Production-grade ML pipeline with custom feature engineering

Architecture:
- Layer 0: Random Forest + HistGradientBoosting
- Layer 1: Logistic Regression (Meta-Learner)
- Custom Feature Engineering with Scikit-Learn Pipelines
- Threshold Optimization for High Recall

Author: Senior Full-Stack AI Engineer & Data Scientist
"""

import pandas as pd
import numpy as np
import joblib
import warnings
import logging
from datetime import datetime
from pathlib import Path
import json

# Scikit-Learn
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report, confusion_matrix, precision_recall_curve, 
    roc_auc_score, f1_score, accuracy_score
)

# Configuration
warnings.filterwarnings('ignore')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ==============================================================================
# CONFIGURATION
# ==============================================================================
class Config:
    """Global configuration"""
    # Paths
    CARD_TRAIN_PATH = Path("../datasets/card/fraudTrain.csv")
    CARD_TEST_PATH = Path("../datasets/card/fraudTest.csv")
    UPI_DATASET_PATH = Path("../datasets/upi/upi_fraud_dataset.csv")
    MODELS_DIR = Path("../models")
    
    # Model files
    MODEL_PATH = MODELS_DIR / "fraud_detection_system.pkl"
    THRESHOLD_PATH = MODELS_DIR / "threshold.txt"
    METADATA_PATH = MODELS_DIR / "model_metadata.json"
    
    # Training parameters
    TEST_SIZE = 0.2
    RANDOM_STATE = 42
    TARGET_RECALL = 0.85  # Aim for 85% recall (catch 85% of fraud)
    
    # Sampling (for faster training on large datasets)
    USE_SAMPLING = True
    SAMPLE_SIZE = 100000


# ==============================================================================
# CUSTOM FEATURE ENGINEERING TRANSFORMER
# ==============================================================================
class TransactionFeatureEngineer(BaseEstimator, TransformerMixin):
    """
    Custom transformer for automated feature engineering.
    Compatible with Scikit-Learn Pipelines.
    
    Features:
    - Time-based feature extraction (hour, day_of_week, is_night, is_weekend)
    - Drops high-cardinality ID columns (noise reduction)
    - Creates domain-specific fraud indicators
    """
    
    def __init__(self, time_col='trans_date_trans_time', dataset_type='card'):
        self.time_col = time_col
        self.dataset_type = dataset_type
        
        # Define columns to drop based on dataset type
        if dataset_type == 'card':
            self.drop_cols = [
                "trans_num", "first", "last", "street", "city", "state",
                "zip", "dob", "unix_time", "cc_num", "trans_date_trans_time"
            ]
        else:  # UPI
            self.drop_cols = [
                "upi_number", "Id", "trans_date_trans_time"
            ]
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X = X.copy()
        
        # 1. Time Feature Extraction
        if self.time_col in X.columns:
            # Convert to datetime if needed
            if pd.api.types.is_object_dtype(X[self.time_col]):
                X[self.time_col] = pd.to_datetime(X[self.time_col], errors='coerce')
            
            # Extract temporal features
            X['hour'] = X[self.time_col].dt.hour
            X['day_of_week'] = X[self.time_col].dt.dayofweek
            X['day_of_month'] = X[self.time_col].dt.day
            X['month'] = X[self.time_col].dt.month
            
            # Domain Knowledge: Fraud patterns
            # Night transactions (00:00 - 05:00) are more suspicious
            X['is_night'] = ((X['hour'] >= 0) & (X['hour'] <= 5)).astype(int)
            
            # Weekend patterns differ
            X['is_weekend'] = (X['day_of_week'] >= 5).astype(int)
            
            # Late night weekend combo (high risk)
            X['is_night_weekend'] = (X['is_night'] & X['is_weekend']).astype(int)
        
        # 2. Amount-based features (if amt column exists)
        if 'amt' in X.columns:
            # Log transform for better distribution
            X['amt_log'] = np.log1p(X['amt'])
            
            # High amount flag (based on domain knowledge)
            X['is_high_amount'] = (X['amt'] > 5000).astype(int)
        
        # 3. Geographic features (for CARD dataset)
        if 'lat' in X.columns and 'long' in X.columns:
            # Distance from origin
            X['distance_from_origin'] = np.sqrt(X['lat']**2 + X['long']**2)
            
            # Merchant distance (if available)
            if 'merch_lat' in X.columns and 'merch_long' in X.columns:
                X['merchant_distance'] = np.sqrt(
                    (X['lat'] - X['merch_lat'])**2 + 
                    (X['long'] - X['merch_long'])**2
                )
        
        # 4. Drop high-cardinality ID columns
        existing_drop_cols = [c for c in self.drop_cols if c in X.columns]
        if existing_drop_cols:
            X = X.drop(columns=existing_drop_cols)
        
        return X


# ==============================================================================
# FRAUD DETECTION SYSTEM
# ==============================================================================
class FraudDetectionSystem:
    """
    Complete fraud detection system with:
    - Automated feature engineering
    - Stacking ensemble (RF + HistGB + LogReg)
    - Threshold optimization
    - Production-ready pipelines
    """
    
    def __init__(self, target_col='is_fraud', dataset_type='card'):
        self.target_col = target_col
        self.dataset_type = dataset_type
        self.model = None
        self.threshold = 0.5
        self.metadata = {}
    
    def load_card_data(self):
        """Load CARD fraud datasets"""
        logging.info("📊 Loading CARD datasets...")
        
        df_train = pd.read_csv(Config.CARD_TRAIN_PATH)
        df_test = pd.read_csv(Config.CARD_TEST_PATH)
        
        logging.info(f"  Train shape: {df_train.shape}")
        logging.info(f"  Test shape: {df_test.shape}")
        
        # Sample if needed
        if Config.USE_SAMPLING and len(df_train) > Config.SAMPLE_SIZE:
            logging.info(f"  Sampling {Config.SAMPLE_SIZE} rows for faster training...")
            df_train = df_train.sample(n=Config.SAMPLE_SIZE, random_state=Config.RANDOM_STATE)
        
        # Combine for single split
        df = pd.concat([df_train, df_test], ignore_index=True)
        
        return df
    
    def load_upi_data(self):
        """Load UPI fraud dataset"""
        logging.info("📊 Loading UPI dataset...")
        
        df = pd.read_csv(Config.UPI_DATASET_PATH)
        logging.info(f"  Dataset shape: {df.shape}")
        
        return df
    
    def build_pipeline(self, X):
        """
        Builds the full Scikit-Learn pipeline dynamically.
        
        Pipeline Structure:
        1. Custom Feature Engineering (TransactionFeatureEngineer)
        2. Column Transformer (Numeric + Categorical processing)
        3. Model (Stacking Ensemble)
        """
        
        # Run dummy transform to identify column types
        temp_engineer = TransactionFeatureEngineer(dataset_type=self.dataset_type)
        X_transformed = temp_engineer.transform(X.head(100))
        
        # Identify numeric and categorical columns
        numeric_features = X_transformed.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_features = X_transformed.select_dtypes(include=['object', 'category']).columns.tolist()
        
        logging.info(f"📋 Numeric features ({len(numeric_features)}): {numeric_features[:10]}...")
        logging.info(f"📋 Categorical features ({len(categorical_features)}): {categorical_features[:10]}...")
        
        # Save metadata
        self.metadata['numeric_features'] = numeric_features
        self.metadata['categorical_features'] = categorical_features
        self.metadata['total_features'] = len(numeric_features) + len(categorical_features)
        
        # --- Build Transformers ---
        
        # Numeric: Impute missing → Scale
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        # Categorical: Impute → Encode (handles unknown categories in production)
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
            ('encoder', OrdinalEncoder(
                handle_unknown='use_encoded_value',
                unknown_value=-1
            ))
        ])
        
        # Combine transformers
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ]
        )
        
        # Complete preprocessing pipeline
        return Pipeline(steps=[
            ('feature_engineering', TransactionFeatureEngineer(dataset_type=self.dataset_type)),
            ('preprocessor', preprocessor)
        ])
    
    def build_stacking_ensemble(self):
        """
        Constructs Stacking Ensemble:
        
        Layer 0 (Base Models):
        - Random Forest: Captures complex non-linear patterns
        - HistGradientBoosting: Fast, accurate, handles missing values
        
        Layer 1 (Meta-Learner):
        - Logistic Regression: Calibrates and combines base model predictions
        """
        
        logging.info("🤖 Building Stacking Ensemble...")
        
        # Base learners
        estimators = [
            ('rf', RandomForestClassifier(
                n_estimators=100,
                max_depth=12,
                min_samples_split=10,
                class_weight='balanced',
                random_state=Config.RANDOM_STATE,
                n_jobs=-1,
                verbose=0
            )),
            ('hgb', HistGradientBoostingClassifier(
                learning_rate=0.05,
                max_iter=200,
                max_depth=10,
                random_state=Config.RANDOM_STATE
            ))
        ]
        
        # Stacking with LogisticRegression as meta-learner
        stacking_clf = StackingClassifier(
            estimators=estimators,
            final_estimator=LogisticRegression(
                class_weight='balanced',
                random_state=Config.RANDOM_STATE,
                max_iter=1000
            ),
            cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=Config.RANDOM_STATE),
            n_jobs=-1,
            verbose=1
        )
        
        logging.info("  ✅ Stacking Ensemble created")
        logging.info("     Layer 0: RandomForest + HistGradientBoosting")
        logging.info("     Layer 1: LogisticRegression (Meta-Learner)")
        
        return stacking_clf
    
    def optimize_threshold(self, y_test, y_proba, target_recall=None):
        """
        Optimizes decision threshold to achieve target recall.
        
        Goal: Maximize precision while maintaining target recall
        (catch X% of fraud cases while minimizing false positives)
        """
        if target_recall is None:
            target_recall = Config.TARGET_RECALL
        
        logging.info(f"🎯 Optimizing threshold for {target_recall*100}% recall...")
        
        precisions, recalls, thresholds = precision_recall_curve(y_test, y_proba)
        
        # Find threshold where recall >= target
        eligible_indices = np.where(recalls >= target_recall)[0]
        
        if len(eligible_indices) > 0:
            # Among eligible thresholds, choose one with highest precision
            best_idx = eligible_indices[np.argmax(precisions[eligible_indices])]
            best_threshold = thresholds[best_idx] if best_idx < len(thresholds) else 0.5
        else:
            logging.warning(f"  ⚠️ Cannot achieve {target_recall*100}% recall, using default 0.5")
            best_threshold = 0.5
        
        logging.info(f"  ✅ Optimal threshold: {best_threshold:.4f}")
        
        return best_threshold
    
    def train(self, data_source='card'):
        """
        Main training pipeline
        
        Args:
            data_source: 'card' or 'upi'
        """
        logging.info("\n" + "="*80)
        logging.info(f"🚀 TRAINING {data_source.upper()} FRAUD DETECTION SYSTEM")
        logging.info("="*80 + "\n")
        
        # 1. Load data
        if data_source == 'card':
            df = self.load_card_data()
        else:
            df = self.load_upi_data()
        
        # Verify target column
        if self.target_col not in df.columns:
            raise ValueError(f"Target column '{self.target_col}' not found in dataset")
        
        X = df.drop(columns=[self.target_col])
        y = df[self.target_col]
        
        logging.info(f"📊 Dataset: {X.shape[0]} samples, {X.shape[1]} features")
        logging.info(f"📊 Class distribution:\n{y.value_counts()}")
        logging.info(f"📊 Fraud rate: {y.mean()*100:.2f}%\n")
        
        # 2. Train-test split (stratified)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=Config.TEST_SIZE,
            stratify=y,
            random_state=Config.RANDOM_STATE
        )
        
        logging.info(f"✂️ Split: Train={len(X_train)}, Test={len(X_test)}\n")
        
        # 3. Build preprocessing pipeline
        preprocessor = self.build_pipeline(X_train)
        
        # 4. Build stacking ensemble
        classifier = self.build_stacking_ensemble()
        
        # 5. Combine into full pipeline
        self.model = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', classifier)
        ])
        
        # 6. Train
        logging.info("\n" + "="*80)
        logging.info("🎯 TRAINING MODEL (this may take a few minutes)...")
        logging.info("="*80 + "\n")
        
        self.model.fit(X_train, y_train)
        
        logging.info("\n✅ Training complete!\n")
        
        # 7. Optimize threshold
        y_proba = self.model.predict_proba(X_test)[:, 1]
        self.threshold = self.optimize_threshold(y_test, y_proba)
        
        # 8. Evaluate
        self.evaluate(X_test, y_test)
        
        # 9. Save
        self.save_model()
    
    def evaluate(self, X_test, y_test):
        """Comprehensive model evaluation"""
        logging.info("\n" + "="*80)
        logging.info("📊 MODEL EVALUATION")
        logging.info("="*80 + "\n")
        
        # Predictions
        y_proba = self.model.predict_proba(X_test)[:, 1]
        y_pred = (y_proba >= self.threshold).astype(int)
        
        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_proba)
        
        # Classification report
        print(classification_report(
            y_test, y_pred,
            target_names=['Legitimate', 'Fraud'],
            digits=4
        ))
        
        # Summary metrics
        logging.info(f"\n📈 Summary Metrics:")
        logging.info(f"   Accuracy:  {accuracy:.4f}")
        logging.info(f"   F1 Score:  {f1:.4f}")
        logging.info(f"   ROC-AUC:   {roc_auc:.4f}")
        logging.info(f"   Threshold: {self.threshold:.4f}")
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        logging.info(f"\n🔢 Confusion Matrix:")
        logging.info(f"   [[TN={cm[0,0]:6d}, FP={cm[0,1]:6d}]")
        logging.info(f"    [FN={cm[1,0]:6d}, TP={cm[1,1]:6d}]]")
        
        # Save metrics
        self.metadata.update({
            'accuracy': float(accuracy),
            'f1_score': float(f1),
            'roc_auc': float(roc_auc),
            'threshold': float(self.threshold),
            'confusion_matrix': cm.tolist()
        })
    
    def save_model(self):
        """Save model and metadata"""
        logging.info("\n" + "="*80)
        logging.info("💾 SAVING MODEL ARTIFACTS")
        logging.info("="*80 + "\n")
        
        # Create directory
        Config.MODELS_DIR.mkdir(exist_ok=True)
        
        # Save model package
        model_package = {
            'model': self.model,
            'threshold': self.threshold,
            'dataset_type': self.dataset_type,
            'training_date': datetime.now().isoformat()
        }
        
        joblib.dump(model_package, Config.MODEL_PATH)
        logging.info(f"✅ Model saved: {Config.MODEL_PATH}")
        
        # Save threshold separately for easy access
        with open(Config.THRESHOLD_PATH, 'w') as f:
            f.write(str(self.threshold))
        logging.info(f"✅ Threshold saved: {Config.THRESHOLD_PATH}")
        
        # Save metadata
        self.metadata['dataset_type'] = self.dataset_type
        self.metadata['training_date'] = datetime.now().isoformat()
        
        with open(Config.METADATA_PATH, 'w') as f:
            json.dump(self.metadata, f, indent=2)
        logging.info(f"✅ Metadata saved: {Config.METADATA_PATH}")
        
        logging.info("\n🎉 All artifacts saved successfully!\n")


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "🚀"*40)
    print("ADVANCED FRAUD DETECTION SYSTEM")
    print("Stacking Ensemble with Custom Feature Engineering")
    print("🚀"*40 + "\n")
    
    # Initialize system
    system = FraudDetectionSystem(
        target_col='is_fraud',
        dataset_type='card'
    )
    
    # Train on CARD dataset
    system.train(data_source='card')
    
    print("\n" + "✅"*40)
    print("TRAINING COMPLETE!")
    print("✅"*40 + "\n")
    
    print("📝 Next steps:")
    print("  1. The backend will automatically load the trained model")
    print("  2. Start backend: python backend/main.py")
    print("  3. Start frontend: cd frontend && npm start")
    print("  4. System will use Stacking Ensemble predictions!")
    print("\n")
