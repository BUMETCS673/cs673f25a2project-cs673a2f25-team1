from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from db import db
from sqlalchemy import text

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration for Azure SQL Database (prod) and SQLite (dev)
# Azure SQL connection string format:
# Server=tcp:{server}.database.windows.net,1433;Initial Catalog={database};Persist Security Info=False;User ID={username};Password={password};MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;
def get_database_uri():
	"""Resolve database URI based on environment.

	- If FLASK_ENV != 'production' or USE_LOCAL_SQLITE is truthy, prefer local SQLite.
	- Otherwise, if all Azure env vars are present, use Azure SQL via pyodbc.
	- Fallback: local SQLite (absolute path) to avoid relative-path issues.
	"""
	env = os.getenv('FLASK_ENV', 'production')
	use_local_sqlite = str(os.getenv('USE_LOCAL_SQLITE', '')).lower() in ('1', 'true', 'yes', 'on')
	base_dir = os.path.dirname(os.path.abspath(__file__))
	sqlite_path = os.path.join(base_dir, 'instance', 'asset_management.db')

	# Development-first: prefer SQLite locally
	if use_local_sqlite:
		# When USE_LOCAL_SQLITE is explicitly set, always use SQLite
		uri = f"sqlite:///{sqlite_path}"
		print(f"Using local SQLite (USE_LOCAL_SQLITE=true): {uri}")
		return uri

	if env != 'production':
		# Allow override via DATABASE_URL if explicitly provided
		if os.getenv('DATABASE_URL'):
			uri = os.getenv('DATABASE_URL')
			print(f"Using DATABASE_URL (dev): {uri}")
			return uri
		# Absolute path ensures consistent resolution regardless of CWD
		uri = f"sqlite:///{sqlite_path}"
		print(f"Using local SQLite (dev): {uri}")
		return uri

	# Production / default: try Azure first
	server = os.getenv('AZURE_SQL_SERVER')
	database = os.getenv('AZURE_SQL_DATABASE')
	username = os.getenv('AZURE_SQL_USERNAME')
	password = os.getenv('AZURE_SQL_PASSWORD')
	if all([server, database, username, password]):
		azure_uri = (
			f"mssql+pyodbc://{username}:{password}@{server}.database.windows.net:1433/{database}"
			"?driver=ODBC+Driver+17+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no&Connection+Timeout=30"
		)
		# If pyodbc is unavailable (e.g., local dev), fall back to SQLite automatically
		try:
			import pyodbc  # type: ignore
			print("Using Azure SQL via pyodbc (prod)")
			return azure_uri
		except Exception:
			fallback = f"sqlite:///{sqlite_path}"
			print(f"pyodbc unavailable; using SQLite fallback: {fallback}")
			return fallback

	# Final fallback: local SQLite
	uri = f"sqlite:///{sqlite_path}"
	print(f"Using default SQLite fallback: {uri}")
	return uri

app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Import models after db is initialized
from models import Portfolio, Asset, Fee, Anomaly

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
	# Lazy import to avoid heavy deps on startup
	from ml.predict import detect_anomalies
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

@app.route('/api/statement-raw', methods=['GET'])
def get_statement_raw():
    limit = int(request.args.get('limit', 5))
    limit = max(1, min(limit, 100))
    rows = []
    try:
        result = db.session.execute(text(f"SELECT TOP {limit} id, line FROM dbo.statement_raw ORDER BY id"))
        for r in result:
            rows.append({'id': int(r.id), 'line': str(r.line)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify(rows)

if __name__ == '__main__':
	with app.app_context():
		try:
			db.create_all()
			print("Database tables created successfully")
		except Exception as e:
			print(f"Database connection error: {e}")
	
	# Azure App Service uses PORT environment variable
	port = int(os.environ.get('PORT', 5000))
	debug = os.environ.get('FLASK_ENV') != 'production'
	
	app.run(host='0.0.0.0', port=port, debug=debug)
