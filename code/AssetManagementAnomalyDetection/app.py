from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime
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
	if env != 'production' or use_local_sqlite:
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
from models import Portfolio, Asset, Fee, Anomaly, ParsedStatement

@app.route('/')
def home():
	return jsonify({'message': 'Asset Management Anomaly Detection API'})

@app.route('/upload')
def upload_page():
	"""Serve the PDF upload web page"""
	return send_from_directory('static', 'upload.html')

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

@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    """
    Upload and process a PDF rental statement using Azure Document Intelligence.
    Falls back to local OCR if Azure is not configured.
    """
    try:
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided',
                'message': 'Please upload a PDF file'
            }), 400

        file = request.files['file']

        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected',
                'message': 'Please select a PDF file to upload'
            }), 400

        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({
                'success': False,
                'error': 'Invalid file type',
                'message': 'Only PDF files are supported'
            }), 400

        # Read file bytes
        pdf_bytes = file.read()

        # Import OCR processor
        from ocr.azure_processor import get_ocr_processor

        # Get appropriate processor (Azure or local fallback)
        processor = get_ocr_processor()

        # Process the PDF
        extracted_data, confidence = processor.process_pdf_bytes(pdf_bytes)

        # Prepare response
        response = {
            'success': True,
            'data': {
                'rent': extracted_data.get('rent'),
                'management_fee': extracted_data.get('management_fee'),
                'repair': extracted_data.get('repair'),
                'deposit': extracted_data.get('deposit'),
                'misc': extracted_data.get('misc'),
                'total': extracted_data.get('total'),
                'date': extracted_data.get('date'),
                'property_id': extracted_data.get('property_id')
            },
            'confidence': round(confidence, 2),
            'method': 'azure' if 'Azure' in processor.__class__.__name__ else 'local',
            'field_confidences': extracted_data.get('field_confidences', {})
        }

        # Log successful processing
        print(f"PDF processed successfully: {file.filename} (confidence: {confidence:.2f})")

        return jsonify(response), 200

    except Exception as e:
        print(f"PDF processing error: {e}")
        return jsonify({
            'success': False,
            'error': 'Processing failed',
            'message': str(e)
        }), 500

@app.route('/api/upload-pdf-batch', methods=['POST'])
def upload_pdf_batch():
    """
    Upload multiple PDF rental statements and store parsed data in database.
    Completely rewrites the parsed_statements table with each batch upload.
    """
    try:
        # Check if files are present
        if 'files' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No files provided',
                'message': 'Please upload PDF files using the "files" field'
            }), 400

        files = request.files.getlist('files')

        if not files or len(files) == 0:
            return jsonify({
                'success': False,
                'error': 'No files selected',
                'message': 'Please select at least one PDF file to upload'
            }), 400

        # Generate batch identifier
        batch_id = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

        # Import OCR processor
        from ocr.azure_processor import get_ocr_processor
        processor = get_ocr_processor()

        # Process all PDFs and collect results
        parsed_records = []
        success_count = 0
        error_count = 0
        errors = []

        for file in files:
            # Validate file type
            if not file.filename.lower().endswith('.pdf'):
                errors.append(f"{file.filename}: Not a PDF file")
                error_count += 1
                continue

            try:
                # Read and process PDF
                pdf_bytes = file.read()
                extracted_data, confidence = processor.process_pdf_bytes(pdf_bytes)

                # Create ParsedStatement record
                statement = ParsedStatement(
                    filename=file.filename,
                    upload_batch=batch_id,
                    property_id=extracted_data.get('property_id'),
                    statement_date=extracted_data.get('date'),
                    rent=extracted_data.get('rent'),
                    management_fee=extracted_data.get('management_fee'),
                    repair=extracted_data.get('repair'),
                    deposit=extracted_data.get('deposit'),
                    misc=extracted_data.get('misc'),
                    total=extracted_data.get('total'),
                    confidence=confidence,
                    processing_method='azure' if 'Azure' in processor.__class__.__name__ else 'local',
                    field_confidences=json.dumps(extracted_data.get('field_confidences', {}))
                )

                parsed_records.append(statement)
                success_count += 1

            except Exception as e:
                errors.append(f"{file.filename}: {str(e)}")
                error_count += 1

        # Store in database (complete rewrite)
        if parsed_records:
            try:
                # Start transaction
                # Clear existing data (complete rewrite for prototype)
                ParsedStatement.query.delete()

                # Add all new records
                for record in parsed_records:
                    db.session.add(record)

                # Commit transaction
                db.session.commit()

                print(f"Stored {len(parsed_records)} parsed statements in batch {batch_id}")

            except Exception as e:
                db.session.rollback()
                return jsonify({
                    'success': False,
                    'error': 'Database error',
                    'message': f'Failed to store parsed data: {str(e)}'
                }), 500

        return jsonify({
            'success': True,
            'batch_id': batch_id,
            'processed': success_count,
            'errors': error_count,
            'error_details': errors,
            'message': f'Successfully processed {success_count} file(s), stored in database'
        }), 200

    except Exception as e:
        print(f"Batch upload error: {e}")
        return jsonify({
            'success': False,
            'error': 'Processing failed',
            'message': str(e)
        }), 500

@app.route('/api/parsed-statements', methods=['GET'])
def get_parsed_statements():
    """
    Retrieve all parsed statement data from the database.
    Supports pagination and filtering.
    """
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        property_id = request.args.get('property_id', None)

        # Build query
        query = ParsedStatement.query

        # Apply filter if provided
        if property_id:
            query = query.filter_by(property_id=property_id)

        # Order by upload time (most recent first)
        query = query.order_by(ParsedStatement.uploaded_at.desc())

        # Paginate results
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        # Format results
        statements = []
        for stmt in paginated.items:
            statements.append({
                'id': stmt.id,
                'filename': stmt.filename,
                'upload_batch': stmt.upload_batch,
                'property_id': stmt.property_id,
                'statement_date': stmt.statement_date,
                'rent': stmt.rent,
                'management_fee': stmt.management_fee,
                'repair': stmt.repair,
                'deposit': stmt.deposit,
                'misc': stmt.misc,
                'total': stmt.total,
                'confidence': stmt.confidence,
                'processing_method': stmt.processing_method,
                'uploaded_at': stmt.uploaded_at.isoformat() if stmt.uploaded_at else None
            })

        return jsonify({
            'success': True,
            'data': statements,
            'total': paginated.total,
            'page': page,
            'per_page': per_page,
            'total_pages': paginated.pages
        }), 200

    except Exception as e:
        print(f"Error fetching parsed statements: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch data',
            'message': str(e)
        }), 500

@app.route('/api/parsed-statements/summary', methods=['GET'])
def get_parsed_statements_summary():
    """
    Get aggregated summary of parsed statement data.
    """
    try:
        # Get all statements
        statements = ParsedStatement.query.all()

        if not statements:
            return jsonify({
                'success': True,
                'summary': {
                    'total_records': 0,
                    'total_properties': 0,
                    'total_rent': 0,
                    'total_fees': 0,
                    'average_confidence': 0,
                    'last_upload': None
                }
            }), 200

        # Calculate aggregates
        properties = set()
        total_rent = 0
        total_fees = 0
        total_confidence = 0
        last_upload = None

        for stmt in statements:
            if stmt.property_id:
                properties.add(stmt.property_id)
            total_rent += stmt.rent or 0
            total_fees += stmt.management_fee or 0
            total_confidence += stmt.confidence or 0
            if not last_upload or stmt.uploaded_at > last_upload:
                last_upload = stmt.uploaded_at

        avg_confidence = total_confidence / len(statements) if statements else 0

        return jsonify({
            'success': True,
            'summary': {
                'total_records': len(statements),
                'total_properties': len(properties),
                'total_rent': round(total_rent, 2),
                'total_management_fees': round(total_fees, 2),
                'average_confidence': round(avg_confidence, 2),
                'last_upload': last_upload.isoformat() if last_upload else None,
                'current_batch': statements[0].upload_batch if statements else None
            }
        }), 200

    except Exception as e:
        print(f"Error generating summary: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate summary',
            'message': str(e)
        }), 500

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
