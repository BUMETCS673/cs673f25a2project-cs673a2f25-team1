from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from db import db

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration for Microsoft SQL Server
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mssql+pyodbc://sa:Sujan210802!@localhost/AYQ?driver=ODBC+Driver+17+for+SQL+Server')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Import models and routes after db is initialized
from models import Portfolio, Asset, Fee, Anomaly
from ml.predict import detect_anomalies

@app.route('/')
def home():
    return jsonify({'message': 'Asset Management Anomaly Detection API'})

@app.route('/api/portfolios', methods=['GET'])
def get_portfolios():
    portfolios = Portfolio.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'manager': p.manager,
        'total_assets': p.total_assets
    } for p in portfolios])

@app.route('/api/anomalies/<int:portfolio_id>', methods=['GET'])
def get_anomalies(portfolio_id):
    anomalies = Anomaly.query.filter_by(portfolio_id=portfolio_id).all()
    return jsonify([{
        'id': a.id,
        'fee_id': a.fee_id,
        'anomaly_score': a.anomaly_score,
        'detected_at': a.detected_at.isoformat()
    } for a in anomalies])

@app.route('/api/detect-anomalies/<int:portfolio_id>', methods=['POST'])
def run_anomaly_detection(portfolio_id):
    # Get fees for the portfolio
    fees = Fee.query.filter_by(portfolio_id=portfolio_id).all()
    fee_data = [{'id': f.id, 'amount': f.amount, 'date': f.date.isoformat()} for f in fees]

    # Run ML detection
    anomalies = detect_anomalies(fee_data)

    # Save anomalies to database
    for anomaly in anomalies:
        new_anomaly = Anomaly(
            portfolio_id=portfolio_id,
            fee_id=anomaly['fee_id'],
            anomaly_score=anomaly['score']
        )
        db.session.add(new_anomaly)
    db.session.commit()

    return jsonify({'message': 'Anomaly detection completed', 'anomalies_found': len(anomalies)})

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Database connection error: {e}")
    app.run(host='0.0.0.0', port=5000, debug=True)
