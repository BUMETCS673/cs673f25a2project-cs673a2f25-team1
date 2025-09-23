import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'anomaly_model.pkl')

def load_or_train_model():
    """Load existing model or train a new one if not exists"""
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    else:
        # Train a basic model with synthetic data for demonstration
        np.random.seed(42)
        # Generate synthetic fee data
        normal_fees = np.random.normal(0.02, 0.005, 1000)  # 2% average fee
        anomalies = np.random.normal(0.10, 0.02, 50)  # Anomalous high fees
        training_data = np.concatenate([normal_fees, anomalies])

        # Train Isolation Forest
        model = IsolationForest(contamination=0.05, random_state=42)
        model.fit(training_data.reshape(-1, 1))

        # Save model
        joblib.dump(model, MODEL_PATH)
        return model

def detect_anomalies(fee_data):
    """
    Detect anomalies in fee data
    Args:
        fee_data: List of dicts with 'id', 'amount', 'date'
    Returns:
        List of anomalies with fee_id and score
    """
    if not fee_data:
        return []

    # Load or train model
    model = load_or_train_model()

    # Prepare data
    df = pd.DataFrame(fee_data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    # Feature engineering
    df['amount_scaled'] = StandardScaler().fit_transform(df[['amount']])

    # Rolling statistics to capture trends
    df['rolling_mean'] = df['amount'].rolling(window=12, min_periods=1).mean()
    df['rolling_std'] = df['amount'].rolling(window=12, min_periods=1).std()

    # Predict anomalies
    predictions = model.predict(df[['amount_scaled']])
    scores = model.decision_function(df[['amount_scaled']])

    # Convert predictions to anomaly scores (lower score = more anomalous)
    anomaly_scores = -scores  # Invert so higher = more anomalous

    anomalies = []
    for i, (pred, score) in enumerate(zip(predictions, anomaly_scores)):
        if pred == -1:  # Anomaly detected
            anomalies.append({
                'fee_id': int(df.iloc[i]['id']),
                'score': float(score),
                'amount': float(df.iloc[i]['amount'])
            })

    return sorted(anomalies, key=lambda x: x['score'], reverse=True)

def retrain_model(new_data):
    """
    Retrain the model with new data
    Args:
        new_data: List of fee amounts
    """
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(np.array(new_data).reshape(-1, 1))
    joblib.dump(model, MODEL_PATH)
    return model
