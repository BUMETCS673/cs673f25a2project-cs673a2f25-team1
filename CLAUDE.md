# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an end-to-end data pipeline for asset management that ingests transactional data from PDF statements with multiple layouts to generate business insights and visualizations. The system consists of:

- **Flask backend** (`code/AssetManagementAnomalyDetection/`) with SQLAlchemy ORM and ML-based anomaly detection
- **React TypeScript frontend** (`code/AssetManagementAnomalyDetection/frontend/`) with Material UI and Chart.js
- **OCR processing utilities** (`code/scripts/`) for parsing rental statements from PDFs
- **Deterministic business analytics** (`code/analysis/`) for computing KPIs from labeled data

## Development Commands

### Backend (Flask API)

**Location:** `code/AssetManagementAnomalyDetection/`

```bash
# Setup
cd code/AssetManagementAnomalyDetection
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Run development server (port 5001 by default)
export FLASK_ENV=development
export PORT=5001
export USE_LOCAL_SQLITE=true
python app.py

# The database will auto-initialize on first run at instance/asset_management.db
```

### Frontend (React)

**Location:** `code/AssetManagementAnomalyDetection/frontend/`

```bash
# Setup
cd code/AssetManagementAnomalyDetection/frontend
npm install

# Run development server
npm start

# Build for production
npm build

# Run tests
npm test
```

**Important:** The frontend proxies API calls to `http://127.0.0.1:5050` (see `frontend/package.json` line 46). If your backend runs on a different port, update the `proxy` field or set `PORT` environment variable for the backend.

### OCR Utilities (Optional)

**Location:** `code/scripts/`

```bash
# Prerequisites: Install Poppler and Tesseract OCR system tools first
pip install pdf2image pytesseract Pillow

# Example usage
cd code/scripts
python ocr_processor_v3.py --property-dir ../../code/sample-data/rental-statements/property-a --output property-a-tuned.csv
```

### Business Analysis (Optional)

**Location:** `code/analysis/`

```bash
# Run deterministic KPI analysis
python code/analysis/business_analyzer.py

# Output: code/analysis/business_analysis_results.json
```

## Architecture

### Backend Architecture

**Entry Point:** `code/AssetManagementAnomalyDetection/app.py`

- **Database Configuration:** `get_database_uri()` function handles multi-environment DB setup:
  - Development: SQLite at `instance/asset_management.db` (default when `FLASK_ENV != 'production'`)
  - Production: Azure SQL Database via pyodbc (requires `AZURE_SQL_*` env vars)
  - Falls back to SQLite if pyodbc is unavailable

- **Database Models:** `models.py` defines SQLAlchemy models:
  - `Portfolio`: Top-level portfolio with manager and total assets
  - `Asset`: Individual assets within portfolios (stocks/securities)
  - `Fee`: Transaction fees associated with portfolios
  - `Anomaly`: Detected anomalies linked to fees and portfolios

- **Database Initialization:** `db.py` exports the SQLAlchemy instance; tables are created via `db.create_all()` in `app.py`

- **ML Pipeline:** `ml/predict.py`:
  - Uses `IsolationForest` from scikit-learn for anomaly detection
  - Model is persisted at `ml/anomaly_model.pkl`
  - `detect_anomalies()` accepts fee data, applies feature engineering (rolling stats), and returns anomalies sorted by score
  - `retrain_model()` allows updating the model with new data

- **OCR Processing Module:** `ocr/processor.py`:
  - Refactored from `code/scripts/ocr_processor_v3.py` for backend API use
  - Extracts financial data from rental statement PDFs
  - Uses `pdftotext` (preferred) or Tesseract OCR (fallback) for text extraction
  - Parses fields: rent, management_fee, repair, deposit, misc, total
  - Returns confidence scores for extracted data and validation notes
  - `process_pdf_from_bytes()` handles uploaded PDF files via API

### Frontend Architecture

**Entry Point:** `code/AssetManagementAnomalyDetection/frontend/src/index.tsx`

- **Main Component:** `App.tsx` is a single-page app with:
  - Portfolio list (sidebar)
  - Selected portfolio details and anomaly visualization (main panel)
  - Chart.js integration for line charts showing anomaly scores over time

- **API Integration:** Uses `axios` for HTTP requests to Flask backend:
  - `GET /api/portfolios` - List all portfolios
  - `GET /api/anomalies/<portfolio_id>` - Get anomalies for a portfolio
  - `POST /api/detect-anomalies/<portfolio_id>` - Trigger ML detection

- **UI Framework:** Material UI v5 with Emotion styling

### OCR Processing Pipeline

**Location:** `code/scripts/`

Three versions available (`ocr_processor_v1.py`, `v2.py`, `v3.py`), with v3 being the most refined:

- Converts PDF pages to images using `pdf2image`
- Performs OCR with `pytesseract`
- Extracts structured data (rent, fees, dates) from rental statements
- Outputs labeled CSV for business analysis

### Business Analysis Module

**Location:** `code/analysis/business_analyzer.py`

- `RentalPropertyAnalyzer` class computes comprehensive KPIs from labeled CSV data:
  - Property-level metrics (rental income, fees, net yield, vacancy rates)
  - Portfolio-level aggregations
  - Seasonal analysis (monthly patterns)
  - Cost optimization opportunities (benchmarking against industry standards)
  - Risk metrics (payment consistency, cost volatility, concentration risk)
  - Predictive analytics (trend analysis and forecasting)

- Data source: Expects `code/sample-data/rental-statements/labels.csv` by default
- Output: `code/analysis/business_analysis_results.json`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/api/portfolios` | List all portfolios |
| GET | `/api/anomalies/<portfolio_id>` | Get anomalies for a portfolio |
| POST | `/api/detect-anomalies/<portfolio_id>` | Run ML anomaly detection and persist results |
| GET | `/api/statement-raw?limit=N` | Get raw statement lines from Azure SQL (uses `TOP N` syntax) |
| POST | `/api/upload-pdf` | Upload PDF file to extract rental statement data via OCR |

### PDF Upload Endpoint Details

**`POST /api/upload-pdf`**

Uploads a PDF file and extracts financial data from rental statements using OCR.

**Request:**
- Content-Type: `multipart/form-data`
- Field: `file` (PDF file)

**Response (Success - 200):**
```json
{
  "success": true,
  "data": {
    "rent": 400.0,
    "management_fee": 40.0,
    "repair": null,
    "deposit": null,
    "misc": null,
    "total": 360.0
  },
  "confidence": 0.84,
  "method": "pdftotext",
  "notes": "",
  "field_confidences": {
    "rent": 0.95,
    "management_fee": 0.95,
    "repair": 0.0,
    "deposit": 0.0,
    "misc": 0.0,
    "total": 0.95
  }
}
```

**Response (Error - 400/500):**
```json
{
  "success": false,
  "error": "Invalid file type",
  "message": "Only PDF files are supported"
}
```

**Testing:**
```bash
curl -X POST http://127.0.0.1:5001/api/upload-pdf \
  -F "file=@/path/to/statement.pdf"
```

**System Dependencies Required:**
- Poppler tools (provides `pdftotext`, `pdftoppm`)
- Tesseract OCR (fallback if pdftotext unavailable)

Install on macOS:
```bash
brew install poppler tesseract
```

Install on Ubuntu/Debian:
```bash
sudo apt-get install poppler-utils tesseract-ocr
```

## Database Configuration

The backend supports two database modes:

1. **SQLite (Development):**
   - No configuration needed
   - Database auto-created at `code/AssetManagementAnomalyDetection/instance/asset_management.db`
   - Force SQLite: `export USE_LOCAL_SQLITE=true`

2. **Azure SQL (Production):**
   ```bash
   export AZURE_SQL_SERVER=your-server
   export AZURE_SQL_DATABASE=your-db
   export AZURE_SQL_USERNAME=your-username
   export AZURE_SQL_PASSWORD=your-password
   ```
   - Requires `pyodbc` and ODBC Driver 17 for SQL Server
   - Connection string uses encryption and timeout of 30s

3. **Custom Database:**
   ```bash
   export DATABASE_URL=your-database-uri
   ```

## Key Files to Understand

- `code/AssetManagementAnomalyDetection/app.py:16-63` - Database configuration logic with environment-based fallbacks
- `code/AssetManagementAnomalyDetection/models.py` - SQLAlchemy schema defining relationships between Portfolio, Asset, Fee, and Anomaly
- `code/AssetManagementAnomalyDetection/ml/predict.py:30-72` - Core anomaly detection algorithm with feature engineering
- `code/AssetManagementAnomalyDetection/frontend/src/App.tsx:83-86` - Portfolio selection triggers anomaly fetch
- `code/analysis/business_analyzer.py:53-106` - Property KPI computation logic with efficiency ratios

## Port Configuration

- **Backend default:** Port 5001 (configurable via `PORT` env var)
- **Frontend default:** Port 3000 (React dev server default)
- **Frontend proxy:** Points to `http://127.0.0.1:5050` - verify this matches backend port

## Testing and Deployment

This codebase does not currently include:
- Automated test suites (no `pytest` or Jest tests found)
- Linting configuration (no `.eslintrc` or `black`/`flake8` setup)
- CI/CD pipelines

### Docker Deployment (with OCR Support)

The backend includes a `Dockerfile` configured with OCR dependencies (Poppler, Tesseract):

**Build and Run Locally:**
```bash
cd code/AssetManagementAnomalyDetection
docker build -t ocr-backend:latest .
docker run -p 8000:8000 -e USE_LOCAL_SQLITE=true ocr-backend:latest
```

**Test PDF Upload:**
```bash
curl -X POST http://localhost:8000/api/upload-pdf \
  -F "file=@../sample-data/rental-statements/property-a/20230725.pdf"
```

### Azure Deployment

For detailed Azure deployment instructions, see `code/AssetManagementAnomalyDetection/AZURE_DEPLOYMENT.md`

**Quick Deploy to Azure Container Instances:**
```bash
# Build and push to Azure Container Registry
az acr build --registry youracr --image ocr-backend:latest .

# Deploy container
az container create \
  --resource-group your-rg \
  --name ocr-backend \
  --image youracr.azurecr.io/ocr-backend:latest \
  --dns-name-label your-app-name \
  --ports 8000
```

**Environment Variables for Production:**
- `FLASK_ENV=production`
- `AZURE_SQL_SERVER`, `AZURE_SQL_DATABASE`, `AZURE_SQL_USERNAME`, `AZURE_SQL_PASSWORD` (for Azure SQL)
- `USE_LOCAL_SQLITE=true` (to use SQLite instead of Azure SQL)

**Note:** Backend uses Gunicorn as WSGI server for production (see `Dockerfile:38`)