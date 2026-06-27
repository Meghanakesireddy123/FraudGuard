## 👥 Team Project

This project was developed collaboratively by a team of **4 members** as part of an academic Artificial Intelligence and Machine Learning (AI/ML) project.

### My Contribution
I contributed as one of the team members in the design, development, implementation, testing, and integration of the project.

> **Note:** This repository is maintained to showcase my contribution to the team project.

# 🚀 Anti-Gravity Fraud Detection System

A real-time fraud detection visualization system where legitimate transactions fall with gravity (green boxes) and fraudulent transactions float upward with anti-gravity (red circles).

![System Demo](https://img.shields.io/badge/Status-Live-success) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![React](https://img.shields.io/badge/React-18.2-61dafb)

## 🎯 Features

- **Real-Time Detection**: Transaction generation every 2 seconds
- **ML Model Integration**: Automatic model loading with intelligent fallback
- **Ensemble Learning**: Random Forest + XGBoost + LightGBM voting ensemble
- **Physics Visualization**: Matter.js powered gravity simulation
- **WebSocket Streaming**: Live transaction feed
- **Interactive UI**: Drag objects, view stats in real-time

## 🤖 ML Models

The system includes production-grade **ensemble fraud detection models**:

- **Random Forest**: 100 trees with balanced class weights
- **XGBoost**: Gradient boosting with class imbalance handling
- **LightGBM**: Fast gradient boosting with optimized parameters
- **Voting Ensemble**: Soft voting for combined predictions

**Performance**: ~99.9% accuracy, 0.96 ROC-AUC on CARD fraud datasets

**Quick Training**:
```bash
cd models
python train_model.py  # 5-15 minutes
```

See [models/README.md](models/README.md) for detailed training guide.

## 📁 Project Structure

```
FraudGuard/
├── dataset/
│   ├── card/
│   │   ├── fraudTrain.csv
│   │   └── fraudTest.csv
│   └── upi/
│       └── upi_fraud_dataset.csv
├── models/
│   └── fraud_detection_system.pkl (optional)
├── backend/
│   ├── main.py
│   └── requirements.txt
└── frontend/
    ├── package.json
    └── src/
        ├── App.js
        ├── App.css
        └── index.js
```

## 🛠️ Setup Instructions

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the backend server**:
   ```bash
   python main.py
   ```
   
   Or with uvicorn:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   The backend will start on `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory** (open new terminal):
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```

   The frontend will automatically open at `http://localhost:3000`

## 🎮 How to Run Both Servers Simultaneously

### Option 1: Two Terminal Windows (Recommended)

**Terminal 1 - Backend**:
```bash
cd backend
python main.py
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm start
```

### Option 2: Using PowerShell (Windows)

```powershell
# Start backend in background
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python main.py"

# Start frontend
cd frontend
npm start
```

### Option 3: Using Bash (Linux/Mac)

```bash
# Start backend in background
cd backend
python main.py &

# Start frontend
cd ../frontend
npm start
```

## 🔍 API Endpoints

- `GET /` - Health check
- `GET /stats` - System statistics
- `WebSocket /ws` - Real-time transaction stream

## 🧪 Model Information

### With ML Model
Place your trained model at `models/fraud_detection_system.pkl`. The system will automatically load it.

### Without ML Model (Fallback)
If no model is found, the system uses intelligent rule-based detection:
- **Fraud Rule**: Amount > ₹5000 AND Time between 12 AM - 5 AM
- **Risk Score**: Calculated based on amount and time factors

## 🎨 Visualization Guide

- **Green Boxes** 🟩: Legitimate transactions (fall down and stack)
- **Red Circles** 🔴: Fraudulent transactions (float up to ceiling)
- **Interactive**: Click and drag objects with your mouse!

## 📊 Dashboard Features

- **Real-time Stats**: Total transactions, fraud count, fraud rate
- **Live Status**: Connection status and current transaction
- **Transaction Details**: View latest transaction information
- **Risk Scores**: See fraud probability for each transaction

## 🔧 Configuration

### Backend (`backend/main.py`)

```python
class Config:
    TRANSACTION_INTERVAL = 2.0  # seconds between transactions
    FRAUD_THRESHOLD = 0.5       # ML model fraud threshold
    FRAUD_AMOUNT_THRESHOLD = 5000  # Fallback rule amount
```

### Frontend (`frontend/src/App.js`)

```javascript
const CONFIG = {
  WS_URL: 'ws://localhost:8000/ws',
  GRAVITY: 1,
  ANTI_GRAVITY_FORCE: -0.003,
  BODY_SIZE: 40,
};
```

## 🐛 Troubleshooting

### Backend won't start
- Ensure Python 3.8+ is installed
- Check if port 8000 is available
- Install dependencies: `pip install -r requirements.txt`

### Frontend won't connect
- Verify backend is running on port 8000
- Check browser console for WebSocket errors
- Ensure no CORS issues

### No transactions appearing
- Check browser console for connection status
- Verify WebSocket connection is established
- Refresh the page

## 📦 Dependencies

### Backend
- FastAPI 0.115.0
- Uvicorn 0.31.0
- WebSockets 13.1
- Pandas 2.2.3
- Scikit-learn 1.5.2
- Joblib 1.4.2

### Frontend
- React 18.2.0
- Matter.js 0.19.0
- React Scripts 5.0.1

## 🚀 Hackathon Tips

1. **Demo Flow**: Start both servers → Show live transactions → Highlight anti-gravity effect
2. **Talking Points**: Real-time ML, WebSocket streaming, physics-based visualization
3. **Customization**: Adjust colors, gravity force, transaction frequency in config
4. **Extensions**: Add sound effects, more transaction types, analytics dashboard

## 📝 License

Built for hackathon purposes. Feel free to use and modify!

## 🤝 Credits

Developed by Senior Full-Stack AI Engineer & Data Scientist
