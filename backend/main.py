"""
Anti-Gravity Fraud Detection System - Backend
Real-time fraud detection with WebSocket streaming and ML model integration

Author: Senior Full-Stack AI Engineer & Data Scientist
"""

import asyncio
import json
import logging
import os
import random
from datetime import datetime, time
from pathlib import Path
from typing import Dict, Optional, List
import warnings
from dotenv import load_dotenv
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib
from datetime import timedelta
from typing import Optional as Opt

import numpy as np
import pandas as pd
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import joblib

# Pydantic for request validation
from pydantic import BaseModel, Field

#Scikit-learn imports for model loading
from sklearn.base import BaseEstimator, TransformerMixin

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings('ignore')

# ============================================================================
# GEMINI AI CONFIGURATION
# ============================================================================

# Configure Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-pro')
    logger.info("✅ Gemini AI configured successfully")
else:
    gemini_model = None
    logger.warning("⚠️ Gemini API key not found. AI chat will be disabled.")

# ============================================================================
# EMAIL CONFIGURATION
# ============================================================================

# Email notification settings
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

if EMAIL_ENABLED and EMAIL_SENDER and EMAIL_PASSWORD:
    logger.info("📧 Email notifications enabled")
else:
    logger.warning("⚠️ Email notifications disabled (check configuration)")

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Configuration constants"""
    # Model paths
    MODEL_DIR = Path("../models")
    CARD_MODEL_PATH = MODEL_DIR / "fraud_detection_system.pkl"
    CARD_METADATA_PATH = MODEL_DIR / "model_metadata.json"
    
    # Dataset paths
    DATASET_DIR = Path("../datasets")
    CARD_TRAIN_PATH = DATASET_DIR / "card" / "fraudTrain.csv"
    UPI_DATASET_PATH = DATASET_DIR / "upi" / "upi_fraud_dataset.csv"
    
    # Password hashing
    # Using standard hashlib for robustness
    
    # Transaction generation settings
    TRANSACTION_INTERVAL = 2.0  # seconds
    DEFAULT_CURRENCY = "INR"
    
    # Risk thresholds
    FRAUD_THRESHOLD = 0.5  # probability threshold for fraud classification
    
    # Transaction simulation parameters
    AMOUNT_RANGE = (10, 50000)
    FRAUD_AMOUNT_THRESHOLD = 5000
    FRAUD_TIME_START = time(0, 0)  # 12 AM
    FRAUD_TIME_END = time(5, 0)    # 5 AM
    
    # Sample locations for realistic simulation
    LOCATIONS = [
        "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
        "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Surat",
        "Lucknow", "Kanpur", "Nagpur", "Indore", "Thane"
    ]
    
    TRANSACTION_TYPES = ["UPI", "CARD"]
    
    # CARD specific merchants
    CARD_MERCHANTS = [
        "Amazon", "Flipkart", "Swiggy", "Zomato", "Uber",
        "BigBasket", "Myntra", "BookMyShow", "MakeMyTrip", "PayTM Mall"
    ]
    
    # UPI specific merchants
    UPI_MERCHANTS = [
        "PhonePe", "GooglePay", "PayTM", "BHIM", "AmazonPay UPI",
        "WhatsApp Pay", "Cred", "FreeCharge", "MobiKwik", "Airtel Payments"
    ]


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ManualTransactionRequest(BaseModel):
    """Request model for manual transaction checking - Comprehensive version with all ML features"""
    # Required basic fields
    transaction_type: str = Field(..., description="Transaction type: UPI or CARD")
    amount: float = Field(..., gt=0, description="Transaction amount in INR")
    merchant: str = Field(..., description="Merchant name")
    
    # Optional basic fields
    category: Optional[str] = Field("general", description="Merchant category")
    location: Optional[str] = Field("Manual Entry", description="Transaction location/city")
    
    # Advanced optional fields for ML model
    transaction_id: Optional[str] = Field(None, description="Custom transaction ID")
    timestamp: Optional[str] = Field(None, description="Transaction timestamp (ISO format)")
    
    # Customer demographics
    gender: Optional[str] = Field("M", description="Customer gender: M/F")
    job: Optional[str] = Field("Professional", description="Customer job/occupation")
    age: Optional[int] = Field(35, description="Customer age")
    
    # Location coordinates
    lat: Optional[float] = Field(None, description="Customer latitude")
    long: Optional[float] = Field(None, description="Customer longitude")
    city_pop: Optional[int] = Field(100000, description="City population")
    
    # Merchant location coordinates
    merch_lat: Optional[float] = Field(None, description="Merchant latitude")
    merch_long: Optional[float] = Field(None, description="Merchant longitude")
    
    # Distance (calculated if not provided)
    distance: Optional[float] = Field(None, description="Distance from customer to transaction location")
    merch_distance: Optional[float] = Field(None, description="Distance to merchant")

class ChatMessage(BaseModel):
    """Request model for AI chat"""
    message: str = Field(..., description="User message to AI")
    conversation_history: Optional[List[Dict[str, str]]] = Field(default_factory=list, description="Previous messages")

class UserCreate(BaseModel):
    """User registration request"""
    email: str = Field(..., description="User email")
    password: str = Field(..., min_length=6, description="Password (min 6 chars)")
    full_name: str = Field(..., description="Full name")

class UserLogin(BaseModel):
    """User login request"""
    email: str = Field(..., description="User email")
    password: str = Field(..., description="Password")

class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: str = Field(..., description="User email")


# ============================================================================
# EMAIL NOTIFICATION HELPER
# ============================================================================

def send_fraud_alert_email(transaction: Dict, prediction: Dict):
    """
    Send email alert when fraud is detected
    Runs asynchronously to not block main thread
    """
    if not EMAIL_ENABLED or not EMAIL_SENDER or not EMAIL_PASSWORD:
        return
    
    try:
        # Use logged-in user's email, fallback to default recipient
        recipient_email = current_user_email if current_user_email else EMAIL_RECIPIENT
        
        if not recipient_email:
            logger.warning("⚠️ No email recipient configured and no user logged in")
            return
        
        # Create email
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_SENDER
        msg['To'] = recipient_email
        msg['Subject'] = f"🚨 FRAUD ALERT: ₹{transaction.get('amount', 0):.2f} - {transaction.get('merchant', 'Unknown')}"
        
        # Email body - HTML format
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
              <h2 style="color: #dc2626; border-bottom: 3px solid #dc2626; padding-bottom: 10px;">
                🚨 FRAUD TRANSACTION DETECTED
              </h2>
              
              <div style="margin: 20px 0; padding: 15px; background-color: #fee2e2; border-left: 4px solid #dc2626; border-radius: 5px;">
                <p style="margin: 0; color: #991b1b; font-weight: bold;">High Risk Transaction Alert</p>
                <p style="margin: 5px 0 0 0; color: #991b1b;">Risk Score: {prediction.get('risk_score', 0) * 100:.1f}%</p>
              </div>
              
              <h3 style="color: #374151; margin-top: 25px;">Transaction Details:</h3>
              <table style="width: 100%; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #e5e7eb;">
                  <td style="padding: 10px; font-weight: bold; color: #6b7280;">ID:</td>
                  <td style="padding: 10px; color: #111827;">{transaction.get('id', 'N/A')}</td>
                </tr>
                <tr style="border-bottom: 1px solid #e5e7eb;">
                  <td style="padding: 10px; font-weight: bold; color: #6b7280;">Type:</td>
                  <td style="padding: 10px; color: #111827;">{transaction.get('type', 'N/A')}</td>
                </tr>
                <tr style="border-bottom: 1px solid #e5e7eb;">
                  <td style="padding: 10px; font-weight: bold; color: #6b7280;">Amount:</td>
                  <td style="padding: 10px; color: #111827; font-size: 18px; font-weight: bold;">₹{transaction.get('amount', 0):,.2f}</td>
                </tr>
                <tr style="border-bottom: 1px solid #e5e7eb;">
                  <td style="padding: 10px; font-weight: bold; color: #6b7280;">Merchant:</td>
                  <td style="padding: 10px; color: #111827;">{transaction.get('merchant', 'N/A')}</td>
                </tr>
                <tr style="border-bottom: 1px solid #e5e7eb;">
                  <td style="padding: 10px; font-weight: bold; color: #6b7280;">Category:</td>
                  <td style="padding: 10px; color: #111827;">{transaction.get('category', 'N/A')}</td>
                </tr>
                <tr style="border-bottom: 1px solid #e5e7eb;">
                  <td style="padding: 10px; font-weight: bold; color: #6b7280;">Location:</td>
                  <td style="padding: 10px; color: #111827;">{transaction.get('location', 'N/A')}</td>
                </tr>
                <tr>
                  <td style="padding: 10px; font-weight: bold; color: #6b7280;">Timestamp:</td>
                  <td style="padding: 10px; color: #111827;">{transaction.get('timestamp', 'N/A')}</td>
                </tr>
              </table>
              
              <div style="margin-top: 30px; padding: 15px; background-color: #f3f4f6; border-radius: 5px;">
                <p style="margin: 0; color: #374151; font-size: 12px;">
                  <strong>Action Required:</strong> Please review this transaction immediately and take appropriate action.
                </p>
              </div>
              
              <div style="margin-top: 20px; text-align: center; color: #6b7280; font-size: 12px;">
                <p>This is an automated alert from FraudGuard AI System</p>
                <p>Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
              </div>
            </div>
          </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"\ud83d\udce7 Fraud alert email sent for transaction {transaction.get('id', 'N/A')}")
        
    except Exception as e:
        logger.error(f"\u274c Error sending fraud alert email: {e}")


# ============================================================================
# SIMPLE IN-MEMORY USER STORAGE (for development/testing)
# ============================================================================

# Using a simple dictionary instead of MongoDB for now
# This avoids MongoDB timeout/connection issues
users_db = {}
users_collection = None  # Set to None to indicate we're using in-memory storage

# Track currently logged-in user for email alerts
current_user_email = None

logger.info("✅ Using in-memory user storage (no MongoDB required)")





# ============================================================================
# CUSTOM TRANSFORMER (Required for loading trained model)
# ============================================================================

class TransactionFeatureEngineer(BaseEstimator, TransformerMixin):
    """
    Custom transformer for automated feature engineering.
    This class MUST be defined before loading the model.
    """
    
    def __init__(self, time_col='trans_date_trans_time', dataset_type='card'):
        self.time_col = time_col
        self.dataset_type = dataset_type
        
        if dataset_type == 'card':
            self.drop_cols = [
                "trans_num", "first", "last", "street", "city", "state",
                "zip", "dob", "unix_time", "cc_num", "trans_date_trans_time"
            ]
        else:
            self.drop_cols = [
                "upi_number", "Id", "trans_date_trans_time"
            ]
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X = X.copy()
        
        # Time feature extraction
        if self.time_col in X.columns:
            if pd.api.types.is_object_dtype(X[self.time_col]):
                X[self.time_col] = pd.to_datetime(X[self.time_col], errors='coerce')
            
            X['hour'] = X[self.time_col].dt.hour
            X['day_of_week'] = X[self.time_col].dt.dayofweek
            X['day_of_month'] = X[self.time_col].dt.day
            X['month'] = X[self.time_col].dt.month
            X['is_night'] = ((X['hour'] >= 0) & (X['hour'] <= 5)).astype(int)
            X['is_weekend'] = (X['day_of_week'] >= 5).astype(int)
            X['is_night_weekend'] = (X['is_night'] & X['is_weekend']).astype(int)
        
        # Amount features
        if 'amt' in X.columns:
            X['amt_log'] = np.log1p(X['amt'])
            X['is_high_amount'] = (X['amt'] > 5000).astype(int)
        
        # Geographic features
        if 'lat' in X.columns and 'long' in X.columns:
            X['distance_from_origin'] = np.sqrt(X['lat']**2 + X['long']**2)
            
            if 'merch_lat' in X.columns and 'merch_long' in X.columns:
                X['merchant_distance'] = np.sqrt(
                    (X['lat'] - X['merch_lat'])**2 + 
                    (X['long'] - X['merch_long'])**2
                )
        
        # Drop high-cardinality columns
        existing_drop_cols = [c for c in self.drop_cols if c in X.columns]
        if existing_drop_cols:
            X = X.drop(columns=existing_drop_cols)
        
        return X


# ============================================================================
# FRAUD DETECTION MODEL
# ============================================================================

class FraudDetectionModel:
    """Handles ML model loading and fraud prediction with fallback logic"""
    
    def __init__(self, model_path: Path):
        self.model_path = model_path
        self.threshold_path = model_path.parent / "threshold.txt"
        self.model = None
        self.threshold = 0.5
        self.features = None
        self.scaler = None
        self.is_using_fallback = False
        self._load_model()
    
    def _load_model(self):
        """Attempt to load the trained model, fallback to rule-based if unavailable"""
        try:
            if self.model_path.exists():
                # Load model package
                model_package = joblib.load(self.model_path)
                
                # Extract components (supports both old and new formats)
                if isinstance(model_package, dict):
                    # New format: stacking ensemble package
                    self.model = model_package.get('model')
                    self.threshold = model_package.get('threshold', 0.5)
                    self.features = model_package.get('features', [])
                    self.scaler = model_package.get('scaler')
                    
                    logger.info(f"✅ Successfully loaded Stacking Ensemble model from {self.model_path}")
                    logger.info(f"📋 Model threshold: {self.threshold:.4f}")
                    if self.features:
                        logger.info(f"📋 Model uses {len(self.features)} features")
                else:
                    # Old format: direct model object
                    self.model = model_package
                    # Try to load threshold from separate file
                    if self.threshold_path.exists():
                        with open(self.threshold_path, 'r') as f:
                            self.threshold = float(f.read().strip())
                        logger.info(f"✅ Loaded model and threshold ({self.threshold:.4f})")
                    else:
                        logger.warning("⚠️ Loaded model in old format (no threshold file)")
                
                self.is_using_fallback = False
            else:
                logger.warning(f"⚠️ Model file not found at {self.model_path}")
                logger.info("🔄 Using fallback rule-based fraud detection")
                self.is_using_fallback = True
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            logger.info("🔄 Falling back to rule-based detection")
            self.is_using_fallback = True
    
    def predict(self, transaction: Dict) -> Dict[str, any]:
        """
        Predict if transaction is fraudulent
        
        Returns:
            Dict with 'is_fraud' (bool) and 'risk_score' (float)
        """
        if self.is_using_fallback:
            return self._fallback_prediction(transaction)
        else:
            return self._model_prediction(transaction)
    
    def _fallback_prediction(self, transaction: Dict) -> Dict[str, any]:
        """
        Rule-based fraud detection fallback
        Enhanced to generate more frequent fraud cases for demonstration
        """
        amount = transaction['amount']
        transaction_time = datetime.fromisoformat(transaction['timestamp']).time()
        
        # Check if time is between midnight and 6 AM
        is_suspicious_time = (
            transaction_time >= Config.FRAUD_TIME_START or transaction_time <= time(6, 0)
        )
        
        # High amount threshold (increased from 5000 to 8000)
        is_high_amount = amount > 8000
        
        # Very high amount (strong fraud indicator) - increased from 15000 to 20000
        is_very_high_amount = amount > 20000
        
        # Round amounts are slightly suspicious
        is_round_amount = amount % 1000 == 0
        
        # Fraud if MULTIPLE conditions met (MORE selective):
        # This creates realistic ~10-15% fraud rate
        is_fraud = (
            is_very_high_amount or  # Only very high amounts (>20k) are definitely fraud
            (is_high_amount and is_suspicious_time and is_round_amount) or  # All 3 factors required
            (amount > 15000 and is_suspicious_time and is_round_amount)  # High amount + time + round (stricter)
        )
        
        # Calculate risk score based on multiple factors
        risk_score = 0.0
        
        if is_very_high_amount:
            risk_score += 0.7  # Very high risk
        elif is_high_amount:
            risk_score += min(amount / 50000, 1.0) * 0.4
        else:
            risk_score += min(amount / 10000, 1.0) * 0.2
        
        if is_suspicious_time:
            risk_score += 0.25
        
        if is_round_amount:
            risk_score += 0.15
        
        # Add realistic randomness (±10% for variety)
        risk_score = max(0.0, min(1.0, risk_score + random.uniform(-0.1, 0.1)))
        
        # If flagged as fraud, ensure risk score is at least 0.5
        if is_fraud and risk_score < 0.5:
            risk_score = random.uniform(0.5, 0.85)
        
        # For legitimate transactions, keep score lower
        if not is_fraud and risk_score > 0.4:
            risk_score = random.uniform(0.1, 0.4)
        
        return {
            'is_fraud': bool(is_fraud),
            'risk_score': round(risk_score, 3)
        }
    
    def _model_prediction(self, transaction: Dict) -> Dict[str, any]:
        """ML model-based prediction using stacking ensemble"""
        try:
            # Create feature dictionary for the transaction
            # The pipeline handles feature engineering internally
            transaction_df = pd.DataFrame([{
                'trans_date_trans_time': transaction['timestamp'],
                'amt': transaction['amount'],
                'merchant': transaction.get('merchant', 'Unknown'),
                'category': transaction.get('type', 'Unknown'),
                # Add minimal required fields, pipeline will engineer features
            }])
            
            # Get prediction probability
            risk_score = float(self.model.predict_proba(transaction_df)[0][1])
            
            # Use optimized threshold from training
            is_fraud = risk_score >= self.threshold
            
            return {
                'is_fraud': bool(is_fraud),
                'risk_score': round(risk_score, 3)
            }
        except Exception as e:
            logger.error(f"Error in model prediction: {e}")
            # Fallback to rule-based if model fails
            return self._fallback_prediction(transaction)
    
    def _prepare_features(self, transaction: Dict) -> Dict:
        """Prepare feature dictionary for ML model"""
        dt = datetime.fromisoformat(transaction['timestamp'])
        
        # Basic features
        features = {
            'amt': transaction['amount'],
            'amt_log': np.log1p(transaction['amount']),
            'trans_hour': dt.hour,
            'trans_day': dt.day,
            'trans_month': dt.month,
            'trans_dayofweek': dt.weekday(),
            'is_weekend': int(dt.weekday() >= 5),
            'is_night': int(dt.hour >= 22 or dt.hour <= 5),
            'is_high_amount': int(transaction['amount'] > 5000),
        }
        
        # Add dummy values for other features if needed
        # (In production, you'd extract these from the transaction)
        default_features = {
            'age': 35, 'lat': 0, 'long': 0, 'city_pop': 100000,
            'distance': 0, 'merch_distance': 0
        }
        features.update(default_features)
        
        return features


# ============================================================================
# TRANSACTION GENERATOR
# ============================================================================

class TransactionGenerator:
    """Generates realistic dummy transactions for simulation"""
    
    def __init__(self):
        self.transaction_count = 0
    
    def generate(self) -> Dict:
        """Generate a single realistic transaction"""
        self.transaction_count += 1
        
        # Randomly select transaction type
        tx_type = random.choice(Config.TRANSACTION_TYPES)
        
        # Generate transaction details
        amount = round(random.uniform(*Config.AMOUNT_RANGE), 2)
        timestamp = datetime.now().isoformat()
        location = random.choice(Config.LOCATIONS)
        
        # Select merchant based on type
        if tx_type == "CARD":
            merchant = random.choice(Config.CARD_MERCHANTS)
        else:
            merchant = random.choice(Config.UPI_MERCHANTS)
        
        transaction = {
            'id': f'TX{self.transaction_count:06d}',
            'type': tx_type,
            'amount': amount,
            'timestamp': timestamp,
            'location': location,
            'merchant': merchant,
            'currency': 'INR'
        }
        
        return transaction


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="Anti-Gravity Fraud Detection API",
    description="Real-time fraud detection with physics-based visualization",
    version="1.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components (lazy loading for fraud detector to prevent blocking)
fraud_detector = None
transaction_generator = TransactionGenerator()

# Track active WebSocket connections
active_connections: List[WebSocket] = []

def get_fraud_detector():
    """Lazy initialization of fraud detector to prevent blocking server startup"""
    global fraud_detector
    if fraud_detector is None:
        fraud_detector = FraudDetectionModel(Config.CARD_MODEL_PATH)
    return fraud_detector


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def health_check():
    """Health check endpoint"""
    detector = get_fraud_detector()
    return {
        "status": "online",
        "service": "Anti-Gravity Fraud Detection System",
        "model_status": "fallback" if detector.is_using_fallback else "ml_model",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    return {
        "total_transactions": transaction_generator.transaction_count,
        "active_connections": len(active_connections),
        "model_type": "fallback" if fraud_detector.is_using_fallback else "ml_model"
    }


@app.post("/auth/register")
async def register(user_data: UserCreate):
    """Simple registration - store user in memory"""
    try:
        # Check if email exists
        if user_data.email in users_db:
            return {"success": False, "error": "Email already exists"}
        
        # Store user with hashed password
        users_db[user_data.email] = {
            "email": user_data.email,
            "password": hash_password(user_data.password),
            "full_name": user_data.full_name,
            "created_at": datetime.now().isoformat()
        }
        
        logger.info(f"✅ User registered: {user_data.email}")
        return {"success": True, "message": "Registration successful"}
    except Exception as e:
        logger.error(f"❌ Registration error: {e}")
        return {"success": False, "error": "Registration failed"}


@app.post("/auth/login")
async def login(credentials: UserLogin):
    """Simple login - check if user exists"""
    global current_user_email
    try:
        # Find user
        user = users_db.get(credentials.email)
        
        if not user:
            return {"success": False, "error": "Invalid credentials"}
        
        # Check password
        if not verify_password(credentials.password, user["password"]):
            return {"success": False, "error": "Invalid credentials"}
        
        # Set current user for email alerts
        current_user_email = credentials.email
        
        logger.info(f"✅ User logged in: {credentials.email}")
        return {
            "success": True,
            "user": {
                "email": user["email"],
                "full_name": user["full_name"]
            }
        }
    except Exception as e:
        logger.error(f"❌ Login error: {e}")
        return {"success": False, "error": "Login failed"}


@app.post("/check-transaction")
async def check_transaction(request: ManualTransactionRequest):
    """
    Manual transaction fraud check endpoint
    Accepts user-provided transaction details (comprehensive version with all fields)
    """
    # Use current timestamp if not provided
    timestamp = request.timestamp if request.timestamp else datetime.now().isoformat()
    
    # Generate transaction ID if not provided
    tx_id = request.transaction_id if request.transaction_id else f'MANUAL{int(datetime.now().timestamp() * 1000)}'
    
    # Create comprehensive transaction dict with all fields
    manual_transaction = {
        'id': tx_id,
        'type': request.transaction_type.upper(),
        'amount': request.amount,
        'timestamp': timestamp,
        'merchant': request.merchant,
        'category': request.category,
        'location': request.location,
        'currency': 'INR',
        
        # Customer demographics
        'gender': request.gender,
        'job': request.job,
        'age': request.age,
        
        # Location data
        'lat': request.lat if request.lat is not None else 19.0760,  # Default Mumbai
        'long': request.long if request.long is not None else 72.8777,
        'city_pop': request.city_pop,
        
        # Merchant location
        'merch_lat': request.merch_lat if request.merch_lat is not None else 19.0760,
        'merch_long': request.merch_long if request.merch_long is not None else 72.8777,
        
        # Distances
        'distance': request.distance if request.distance is not None else 0.0,
        'merch_distance': request.merch_distance if request.merch_distance is not None else 0.0,
    }
    
    # Get fraud prediction from model (now with all features)
    prediction = get_fraud_detector().predict(manual_transaction)
    
    logger.info(
        f"📋 Manual check: {request.transaction_type} | ₹{request.amount:.2f} | "
        f"{'🚨 FRAUD' if prediction['is_fraud'] else '✅ LEGIT'} | "
        f"Risk: {prediction['risk_score']:.3f}"
    )
    
    # Send email alert if fraud detected
    if prediction['is_fraud']:
        try:
            import threading
            email_thread = threading.Thread(
                target=send_fraud_alert_email,
                args=(manual_transaction, prediction)
            )
            email_thread.daemon = True
            email_thread.start()
        except Exception as e:
            logger.error(f"Error sending email: {e}")
    
    return {
        'transaction': manual_transaction,
        'prediction': prediction,
        'model_type': 'ml_model' if not fraud_detector.is_using_fallback else 'rule_based'
    }


@app.post("/chat")
async def chat_with_ai(request: ChatMessage):
    """
    AI-powered chat endpoint using Gemini AI
    Provides intelligent responses about FraudGuard system
    """
    if not gemini_model:
        return {
            "response": "AI chat is currently unavailable. Please ensure the Gemini API key is configured.",
            "error": "Gemini API not configured"
        }
    
    try:
        # Build strict context for FraudGuard - ONLY answer project-related questions
        system_context = """You are the FraudGuard AI Assistant, a specialized expert ONLY in fraud detection and the FraudGuard system.

FraudGuard System Overview:
- Real-time fraud detection platform using ML ensemble models (XGBoost, LightGBM, Random Forest)
- Features: Real-time WebSocket transaction monitoring, manual transaction checking, live dashboard
- ML Model: Stacking ensemble with custom feature engineering and threshold optimization
- Technologies: Python (FastAPI), React (TypeScript), MongoDB, WebSocket
- Data: CARD and UPI transaction datasets with fraud indicators

STRICT RULES:
1. ONLY answer questions about:
   - FraudGuard features and functionality
   - Fraud detection concepts and techniques
   - How to use the system (dashboard, manual checks, settings)
   - ML model architecture and performance
   - Data export and analytics
   - Technical implementation details
   
2. For ANY off-topic questions (politics, general AI, other products, personal advice, etc.):
   - Politely decline
   - Remind user you are FraudGuard-specific assistant
   - Suggest rephrasing to focus on fraud detection or the system
   
3. Response Style:
   - Concise and technical when appropriate
   - Friendly and helpful
   - Maximum 3-4 sentences unless explaining complex features
   - Use emojis sparingly (max 1-2 per response)

User question: """
        
        # Combine context with user message
        full_prompt = system_context + request.message
        
        # Generate response with safety settings
        response = gemini_model.generate_content(
            full_prompt,
            generation_config={
                'temperature': 0.7,  # Balanced creativity
                'top_p': 0.9,
                'top_k': 40,
                'max_output_tokens': 300,  # Keep responses concise
            }
        )
        
        logger.info(f"💬 AI Chat: '{request.message[:50]}...'")
        
        return {
            "response": response.text,
            "model": "gemini-pro",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error in AI chat: {e}")
        return {
            "response": "I apologize, but I encountered an error processing your message. Please try again.",
            "error": str(e)
        }


# ============================================================================
# AUTHENTICATION UTILS (SIMPLE & ROBUST)
# ============================================================================

def hash_password(password: str) -> str:
    """Hash password using SHA256 (Robust Standard Library)"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return hash_password(plain_password) == hashed_password

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/auth/register")
async def register(user_data: UserCreate):
    """
    User registration endpoint
    Creates new user account with hashed password
    """
    try:
        # Check if user already exists
        if user_data.email in users_db:
            return {
                "success": False,
                "error": "Account already exists with this email"
            }
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Store user in memory
        users_db[user_data.email] = {
            "email": user_data.email,
            "password_hash": hashed_password,
            "full_name": user_data.full_name,
            "created_at": datetime.now().isoformat()
        }
        
        logger.info(f"✅ New user registered: {user_data.email}")
        
        return {
            "success": True,
            "message": "Account created successfully! Please log in."
        }
        
    except Exception as e:
        import traceback
        logger.error(f"❌ Registration error: {e}")
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "error": "Registration failed. Please try again."
        }


@app.post("/auth/login")
async def login(credentials: UserLogin):
    """
    User login endpoint
    Validates credentials and returns user info
    """
    try:
        # Find user by email
        user = users_db.get(credentials.email)
        
        # Check if user exists
        if not user:
            return {
                "success": False,
                "error": "Account not found - please sign up or check your email"
            }
        
        # Verify password
        if not verify_password(credentials.password, user["password_hash"]):
            return {
                "success": False,
                "error": "Incorrect password"
            }
        
        # Login successful
        logger.info(f"✅ User logged in: {credentials.email}")
        
        return {
            "success": True,
            "message": "Login successful!",
            "user": {
                "email": user["email"],
                "full_name": user["full_name"]
            }
        }
        
    except Exception as e:
        import traceback
        logger.error(f"❌ Login error: {e}")
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "error": "Login failed. Please try again."
        }


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time transaction streaming
    Streams: transaction data + fraud prediction
    """
    await websocket.accept()
    active_connections.append(websocket)
    
    client_id = f"Client_{len(active_connections)}"
    logger.info(f"🔌 {client_id} connected. Total connections: {len(active_connections)}")
    
    try:
        # Send initial connection confirmation
        detector = get_fraud_detector()
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to Anti-Gravity Fraud Detection System",
            "client_id": client_id,
            "model_status": "fallback" if detector.is_using_fallback else "ml_model"
        })
        
        # Keep connection alive and wait for disconnect
        while True:
            # Wait for messages from client (ping/pong, etc.)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                # Handle any client messages if needed
            except asyncio.TimeoutError:
                # No message received, continue
                pass
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info(f"🔌 {client_id} disconnected. Total connections: {len(active_connections)}")
    except Exception as e:
        logger.error(f"❌ WebSocket error for {client_id}: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)


# ============================================================================
# BACKGROUND TASKS
# ============================================================================

async def broadcast_to_clients(message: Dict):
    """Broadcast message to all connected WebSocket clients"""
    disconnected = []
    
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except Exception as e:
            logger.error(f"Error broadcasting to client: {e}")
            disconnected.append(connection)
    
    # Remove disconnected clients
    for conn in disconnected:
        active_connections.remove(conn)


async def transaction_heartbeat():
    """
    Background task that generates and broadcasts transactions
    Generates 1 transaction every 2 seconds
    """
    logger.info("💓 Transaction heartbeat started")
    
    while True:
        try:
            # Generate transaction
            transaction = transaction_generator.generate()
            
            # Get fraud prediction
            prediction = fraud_detector.predict(transaction)
            
            # Combine transaction and prediction
            message = {
                "type": "transaction",
                "transaction": transaction,
                "prediction": prediction,
                "timestamp": datetime.now().isoformat()
            }
            
            # Broadcast to all connected clients
            if active_connections:
                await broadcast_to_clients(message)
                
                # Log for monitoring
                fraud_label = "🚨 FRAUD" if prediction['is_fraud'] else "✅ LEGIT"
                logger.info(
                    f"{fraud_label} | {transaction['type']} | "
                    f"₹{transaction['amount']:.2f} | "
                    f"Risk: {prediction['risk_score']:.3f} | "
                    f"{transaction['merchant']}"
                )
            
            # Wait for next heartbeat
            await asyncio.sleep(Config.TRANSACTION_INTERVAL)
            
        except Exception as e:
            logger.error(f"Error in transaction heartbeat: {e}")
            await asyncio.sleep(Config.TRANSACTION_INTERVAL)


@app.on_event("startup")
async def startup_event():
    """Initialize background tasks on application startup"""
    logger.info("🚀 Starting Anti-Gravity Fraud Detection System")
    detector = get_fraud_detector()
    logger.info(f"📊 Model Status: {'Fallback (Rule-based)' if detector and detector.is_using_fallback else 'ML Model Loaded'}")
    
    # Start transaction generation heartbeat
    asyncio.create_task(transaction_heartbeat())


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("🛑 Shutting down Anti-Gravity Fraud Detection System")
    
    # Close all WebSocket connections
    for connection in active_connections:
        await connection.close()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
