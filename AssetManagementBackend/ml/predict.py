import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os
import random as rand

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

def detect_anomalies(fee_data, contamination=0.05, random_state=42):
    """
    Detect anomalies in fee data using advanced ML techniques
    Args:
        fee_data: List of dicts with 'id', 'amount', 'date'
        contamination: Expected proportion of anomalies (default 5%)
        random_state: Random seed for reproducibility
    Returns:
        List of anomalies with fee_id and score
    """
    if not fee_data or len(fee_data) < 2:
        return []

    # Prepare data
    df = pd.DataFrame(fee_data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    # Advanced feature engineering
    scaler = StandardScaler()
    df['amount_scaled'] = scaler.fit_transform(df[['amount']])

    # Rolling statistics to capture trends (handle smaller datasets)
    window_size = min(12, len(df))  # Use smaller window for small datasets
    df['rolling_mean'] = df['amount'].rolling(window=window_size, min_periods=1).mean()
    df['rolling_std'] = df['amount'].rolling(window=window_size, min_periods=1).std()

    # Relative deviation from rolling mean
    df['relative_deviation'] = (df['amount'] - df['rolling_mean']) / df['rolling_std'].replace(0, 1)

    # First derivative (rate of change)
    df['first_derivative'] = df['amount'].diff().fillna(0)

    # Handle NaN values properly (avoid pandas warning)
    df = df.fillna(0)

    # Prepare features for ML model
    features = ['amount_scaled', 'relative_deviation', 'first_derivative']

    # Create and fit multiple models for better detection
    models = []
    scores_history = []

    # Use different contamination levels to capture various anomaly types
    contamination_levels = [contamination, contamination * 0.5, contamination * 1.5]
    contamination_levels = [max(0.01, min(0.5, c)) for c in contamination_levels]  # Keep within bounds

    for i, level in enumerate(contamination_levels):
        current_seed = random_state + i
        model = IsolationForest(contamination=level, random_state=current_seed, n_estimators=100)
        model.fit(df[features])

        predictions = model.predict(df[features])
        scores = model.decision_function(df[features])
        scores_history.append(scores)

        models.append(model)

    # Combine scores from multiple models for better anomaly detection
    combined_scores = np.mean(scores_history, axis=0)
    combined_scores = -combined_scores  # Invert so higher = more anomalous

    # Use ensemble voting for better anomaly detection
    all_predictions = np.array([model.predict(df[features]) for model in models]).T
    ensemble_predictions = np.where(np.sum(all_predictions == -1, axis=1) >= 2, -1, 1)  # Majority vote

    anomalies = []
    for i, (pred, score) in enumerate(zip(ensemble_predictions, combined_scores)):
        if pred == -1:  # Anomaly detected by ensemble
            # Original simple scoring - just the ML-calculated scores
            anomalies.append({
                'fee_id': int(df.iloc[i]['id']),
                'score': float(score),
                'amount': float(df.iloc[i]['amount'])
            })

    # Sort by score (highest first) - return to original simpler approach
    anomalies_sorted = sorted(anomalies, key=lambda x: x['score'], reverse=True)

    # Return all anomalies without overriding to get original ML-calculated scores
    return anomalies_sorted

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
