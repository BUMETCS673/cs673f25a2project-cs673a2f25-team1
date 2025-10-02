from db import db
from datetime import datetime

class Portfolio(db.Model):
    __tablename__ = 'portfolios'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    manager = db.Column(db.String(100), nullable=False)
    total_assets = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    assets = db.relationship('Asset', backref='portfolio', lazy=True)
    fees = db.relationship('Fee', backref='portfolio', lazy=True)
    anomalies = db.relationship('Anomaly', backref='portfolio', lazy=True)

class Asset(db.Model):
    __tablename__ = 'assets'

    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=True)
    purchase_date = db.Column(db.Date, nullable=False)

class Fee(db.Model):
    __tablename__ = 'fees'

    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    fee_type = db.Column(db.String(50), nullable=False)  # e.g., 'management', 'performance'
    description = db.Column(db.Text, nullable=True)

class Anomaly(db.Model):
    __tablename__ = 'anomalies'

    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'), nullable=False)
    fee_id = db.Column(db.Integer, db.ForeignKey('fees.id'), nullable=False)
    anomaly_score = db.Column(db.Float, nullable=False)
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed = db.Column(db.Boolean, default=False)

    # Relationship to fee
    fee = db.relationship('Fee', backref='anomalies')

class ParsedStatement(db.Model):
    """
    Store parsed rental statement data from PDF uploads.
    This table gets completely rewritten with each new batch upload (prototype approach).
    """
    __tablename__ = 'parsed_statements'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)  # Source PDF filename
    upload_batch = db.Column(db.String(100), nullable=False)  # Batch identifier (timestamp-based)

    # Property and date info
    property_id = db.Column(db.String(255), nullable=True)  # Address/Property identifier
    statement_date = db.Column(db.String(50), nullable=True)  # Date from the statement

    # Financial data
    rent = db.Column(db.Float, nullable=True)
    management_fee = db.Column(db.Float, nullable=True)
    repair = db.Column(db.Float, nullable=True)
    deposit = db.Column(db.Float, nullable=True)
    misc = db.Column(db.Float, nullable=True)
    total = db.Column(db.Float, nullable=True)

    # Metadata
    confidence = db.Column(db.Float, nullable=True)  # OCR confidence score
    processing_method = db.Column(db.String(50), nullable=True)  # 'azure' or 'local'
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Additional fields for debugging/auditing
    raw_text = db.Column(db.Text, nullable=True)  # Optional: store raw extracted text
    field_confidences = db.Column(db.Text, nullable=True)  # JSON string of per-field confidence
