# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## ⚠️ CRITICAL: Azure Deployment Safety

**BEFORE making ANY Azure changes, read this:**

### Common Deployment Errors to Avoid
- ❌ **Never change resource group** - Always use `asset-management-rg-v2`
- ❌ **Never change ACR registry name** - Always use `assetmgmtsuiacr.azurecr.io`
- ❌ **Never change database server** - Always use `ocr-backend-sql/OCRDatabase`
- ❌ **Never force-push to ACR** - Can break production deployment
- ❌ **Never modify App Service without backup plan** - Always verify in staging first

### Safe Deployment Checklist
- [ ] Verify you're targeting `asset-management-rg-v2` resource group
- [ ] Build Docker image with `--platform linux/amd64` (for ARM64 hosts)
- [ ] Tag image correctly: `assetmgmtsuiacr.azurecr.io/<image-name>:<tag>`
- [ ] Test image locally first: `docker run -p 5000:5000 <image>`
- [ ] Push to ACR: `az acr login --name assetmgmtsuiacr`
- [ ] Verify deployment in Azure Portal before declaring success
- [ ] Check App Service logs: `az webapp log tail --name ocr-backend-app --resource-group asset-management-rg-v2`

### Azure Configuration Constants (DO NOT CHANGE)
```bash
RESOURCE_GROUP="asset-management-rg-v2"           # FIXED - never change
ACR_NAME="assetmgmtsuiacr"                        # FIXED - never change
ACR_LOGIN_SERVER="assetmgmtsuiacr.azurecr.io"    # FIXED - never change
APP_NAME="ocr-backend-app"                        # FIXED - never change
DB_SERVER="ocr-backend-sql"                       # FIXED - never change
DB_NAME="OCRDatabase"                             # FIXED - never change
REGION="centralus"                                # FIXED - never change
```

### Deployment Troubleshooting
**If deployment fails:**
1. Check App Service logs: `az webapp log tail --name ocr-backend-app --resource-group asset-management-rg-v2`
2. Verify image exists in ACR: `az acr repository show-tags --name assetmgmtsuiacr --repository <image-name>`
3. Restart App Service: `az webapp restart --name ocr-backend-app --resource-group asset-management-rg-v2`
4. Verify environment variables: `az webapp config appsettings list --name ocr-backend-app --resource-group asset-management-rg-v2`

**Rollback procedure:**
```bash
# Find previous working image tag
az acr repository show-tags --name assetmgmtsuiacr --repository ocr-backend --orderby time_desc

# Deploy previous tag
az webapp config container set \
  --name ocr-backend-app \
  --resource-group asset-management-rg-v2 \
  --docker-custom-image-name assetmgmtsuiacr.azurecr.io/ocr-backend:<previous-tag>

# Restart and verify
az webapp restart --name ocr-backend-app --resource-group asset-management-rg-v2
```

---

## Quick Reference

### Essential Commands
```bash
# Backend (Development)
cd code/AssetManagementAnomalyDetection
python app.py  # Runs on http://127.0.0.1:5050

# Frontend (Development)
cd code/AssetManagementAnomalyDetection/frontend
npm start  # Runs on http://localhost:3000, proxies API to :5050

# Business Analysis
python analysis/business_analyzer.py  # Outputs to analysis/business_analysis_results.json
```

### Key Ports & URLs
- **Dev Backend**: http://127.0.0.1:5050
- **Dev Frontend**: http://localhost:3000 (proxies to :5050)
- **Production**: https://ocr-backend-app.azurewebsites.net

### Database Quick Switch
```bash
# Local SQLite (Development)
export USE_LOCAL_SQLITE=true
export FLASK_ENV=development

# Azure SQL (Production)
export FLASK_ENV=production
# Credentials in .env file (never commit)
```

### Critical Patterns (Must Follow)
- **Layering**: API → business_logic → db (STRICT - no violations)
- **SQL**: Always parameterize queries (never string concatenation)
- **Testing**: ≥80% coverage (≥90% for critical paths)
- **Complexity**: ≤10 cyclomatic complexity per function
- **PRs**: ≤400 LOC (justify if >800)
- **Type hints**: Required on all Python functions
- **Error handling**: No bare `except` - always catch specific exceptions

### Common Gotchas
- ⚠️ Frontend proxy expects backend on port **5050** (not 5000)
- ⚠️ ARM64 Docker builds need `--platform linux/amd64` for Azure
- ⚠️ Azure deployments MUST use `asset-management-rg-v2` resource group
- ⚠️ OCR falls back to local Tesseract if Azure credentials missing
- ⚠️ ML model loads lazily on first anomaly detection request

---

## Table of Contents

1. [Critical: Azure Deployment Safety](#️-critical-azure-deployment-safety)
2. [Quick Reference](#quick-reference)
3. [Project Overview](#project-overview)
4. [Repository Structure](#repository-structure)
5. [Technology Stack](#technology-stack)
6. [Architecture & Data Flow](#architecture--data-flow)
7. [Development Setup](#development-setup)
8. [Database Schema](#database-schema)
9. [API Endpoints](#api-endpoints)
10. [Coding Standards](#coding-standards)
11. [Testing Requirements](#testing-requirements)
12. [Security & Secrets](#security--secrets)
13. [Performance Guidelines](#performance-guidelines)
14. [Code Review Checklist](#code-review-checklist)
15. [Deployment & Azure](#deployment--azure)
16. [Troubleshooting](#troubleshooting)
17. [Additional Resources](#additional-resources)

---

## Project Overview

An end-to-end data pipeline that ingests transactional data from PDF statements with multiple layouts, performs OCR and parsing, generates business insights, and provides anomaly detection for rental property management. The system includes a Flask backend with SQLAlchemy, a React TypeScript frontend, and optional OCR utilities with deterministic business analysis capabilities.

---

## Repository Structure

```
<project-root>/
├── code/
│   ├── AssetManagementAnomalyDetection/   # Main web application
│   │   ├── app.py                          # Flask API entrypoint (470 lines)
│   │   ├── models.py                       # SQLAlchemy models (Portfolio, Asset, Fee, Anomaly, ParsedStatement)
│   │   ├── db.py                           # Database initialization
│   │   ├── requirements.txt                # Python dependencies
│   │   ├── Dockerfile                      # Container configuration
│   │   ├── startup.sh                      # Azure App Service startup script
│   │   ├── ml/                             # Machine learning artifacts
│   │   │   ├── anomaly_model.pkl           # Pre-trained Isolation Forest model
│   │   │   └── predict.py                  # ML inference logic
│   │   ├── ocr/                            # OCR processing utilities
│   │   │   ├── azure_processor.py          # Azure Document Intelligence integration
│   │   │   ├── ocr_processor_v1.py         # Local OCR (Tesseract)
│   │   │   ├── ocr_processor_v2.py         # Enhanced local OCR
│   │   │   ├── ocr_processor_v3.py         # Latest local OCR version
│   │   │   └── test_pdf_upload.html        # OCR testing interface
│   │   ├── frontend/                       # React TypeScript application
│   │   │   ├── package.json                # Node.js dependencies and scripts
│   │   │   └── src/
│   │   │       ├── App.tsx                 # Main React component
│   │   │       ├── index.tsx               # React entry point
│   │   │       └── index.css               # Global styles
│   │   ├── scripts/                        # Data transformation utilities
│   │   │   ├── ingest_statement_csv_to_azure.py    # CSV ingestion
│   │   │   ├── transform_statement_entries_to_fees.py  # Entry to fee transformation
│   │   │   └── upload_statement_raw.py     # Raw statement upload
│   │   ├── instance/                       # SQLite database (dev)
│   │   │   └── asset_management.db
│   │   ├── static/                         # Static files
│   │   │   └── upload.html                 # PDF upload interface
│   │   ├── azure-deployment/               # Azure deployment configuration
│   │   └── db_init.sql                     # SQL Server schema initialization
│   ├── AzureFunctionsApi/                  # Azure Functions API
│   ├── ocr/                                # OCR module (legacy/shared)
│   └── sample-data/                        # Sample datasets
│       └── rental-statements/
├── analysis/                               # Deterministic business analysis
│   ├── business_analyzer.py                # KPI analytics engine
│   ├── examples.py                         # Usage examples
│   ├── README.md                           # Analysis engine documentation
│   └── business_analysis_results.json      # Sample output
├── README.md                               # Main repository documentation
├── PRD.md                                  # Product requirements document
└── TEAM.md                                 # Team members
```

---

## Technology Stack

### Backend
- **Language**: Python 3.9+
- **Framework**: Flask 2.3.3+
- **ORM**: Flask-SQLAlchemy 3.0.5+
- **Database**:
  - Development: SQLite 3 (instance/asset_management.db)
  - Production: Azure SQL Database (via pyodbc 4.0.34+)
- **ML Framework**: scikit-learn 1.4.0+ (Isolation Forest)
- **OCR**:
  - Azure Document Intelligence (azure-ai-formrecognizer 3.3.0+)
  - Local fallback: Tesseract + pdf2image
- **Data Processing**: pandas 2.1.0+, numpy 1.25.0+
- **Server**: Gunicorn 21.2.0+ (production)
- **CORS**: Flask-CORS 4.0.0+

### Frontend
- **Language**: TypeScript 4.9.5+
- **Framework**: React 18.2.0
- **UI Library**: Material-UI (MUI) 5.14.2+
- **Charts**: Chart.js 4.3.0 + react-chartjs-2 5.2.0
- **HTTP Client**: Axios 1.4.0
- **Build Tool**: react-scripts 5.0.1
- **Date Utilities**: date-fns 2.30.0

### Deployment
- **Platform**: Azure App Service (Linux, Docker)
- **Container Registry**: Azure Container Registry (assetmgmtsuiacr.azurecr.io)
- **Database**: Azure SQL Database (Server: ocr-backend-sql, DB: OCRDatabase)
- **Region**: Central US
- **App URL**: https://ocr-backend-app.azurewebsites.net

---

## Architecture & Data Flow

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  React TypeScript + MUI + Chart.js                          │
│  (Deployed to Azure Static Web Apps)                        │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTP/REST
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                      Flask Backend                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  API Routes  │  │   ML Module  │  │  OCR Module  │      │
│  │  (app.py)    │  │  (predict.py)│  │  (azure_proc)│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                   │                  │             │
│         └───────────────────┴──────────────────┘             │
│                             │                                │
│                    ┌────────▼────────┐                       │
│                    │   SQLAlchemy    │                       │
│                    │   (ORM Layer)   │                       │
│                    └────────┬────────┘                       │
└─────────────────────────────┼────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Database Layer                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Development: SQLite (instance/asset_management.db)  │   │
│  │  Production:  Azure SQL Database (ocr-backend-sql)   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   External Services                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Azure Document Intelligence API (OCR)                │  │
│  │  Fallback: Local Tesseract + pdf2image               │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Layering Rules (STRICT ENFORCEMENT)

```
┌─────────────────────────────────────┐
│  API Layer (app.py, api/)           │  ← HTTP endpoints only
└────────────────┬────────────────────┘
                 ↓ (calls)
┌─────────────────────────────────────┐
│  Business Logic Layer               │  ← Domain rules, calculations
└────────────────┬────────────────────┘
                 ↓ (calls)
┌─────────────────────────────────────┐
│  Database Layer (db/, models.py)    │  ← Data persistence only
└─────────────────────────────────────┘
```

**Forbidden Patterns:**
- ❌ Database layer importing from API layer
- ❌ Business logic importing from API layer
- ❌ Circular dependencies between modules
- ❌ Direct database access from API routes (must go through business logic)

### Data Flow

1. **Statement Ingestion**:
   - User uploads PDF via `/api/upload-pdf` or `/api/upload-pdf-batch`
   - OCR processor extracts text using Azure Document Intelligence (or local Tesseract fallback)
   - Parsed data stored in `parsed_statements` table

2. **Fee Transformation**:
   - Scripts in `scripts/` transform `statement_entries` → `fees`
   - Maps rent → rental_income, management_fee → mgmt_fee, etc.
   - Processes in batches of 100 records

3. **Anomaly Detection**:
   - ML module (`ml/predict.py`) uses Isolation Forest algorithm
   - Detects anomalously high management fees per portfolio
   - Features: amount_scaled, rolling_mean, rolling_std (12-period window)
   - Results stored in `anomalies` table with scores

4. **Business Analytics** (Deterministic):
   - `analysis/business_analyzer.py` computes KPIs from labeled CSV
   - Metrics: rental income, management fee ratio, repair cost ratio, net yield, cash flow, vacancy rate
   - Outputs: property-level KPIs, portfolio metrics, seasonal analysis, cost optimization, risk metrics, predictive analytics

### Key Patterns & Conventions

1. **Database Connection Strategy**: The application uses smart database resolution (`get_database_uri()` in `app.py`):
   - Development mode (`FLASK_ENV != production`) or `USE_LOCAL_SQLITE=true` → SQLite
   - Production mode with Azure SQL credentials → Azure SQL via pyodbc
   - Fallback: SQLite (absolute path to avoid CWD issues)

2. **OCR Processor Selection**: The `ocr.azure_processor.get_ocr_processor()` function automatically selects:
   - **Azure Document Intelligence**: if `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` and `AZURE_DOCUMENT_INTELLIGENCE_KEY` are set
   - **Local Tesseract**: fallback if Azure credentials are missing

3. **Frontend API Proxy**: The React frontend (`frontend/package.json`) has a proxy configuration:
   ```json
   "proxy": "http://127.0.0.1:5050"
   ```
   This proxies all API requests to the backend. If backend runs on a different port, update this value.

4. **ML Model Lifecycle**:
   - Pre-trained model: `ml/anomaly_model.pkl`
   - Auto-loads on first anomaly detection request
   - If missing, trains on synthetic data (normal fees ~2%, anomalies ~10%)
   - Contamination rate: 5%
   - Can retrain with `retrain_model()` function

5. **Batch Upload Pattern**: The `upload_pdf_batch` endpoint:
   - Generates unique batch ID: `YYYYMMDD_HHMMSS`
   - Processes all PDFs in parallel
   - Stores each result in `parsed_statements` table
   - Returns summary: success count, error count, batch ID

6. **Common Implementation Patterns**:
   - **Lazy imports**: ML module imported on-demand to avoid heavy startup deps
   - **Absolute paths**: SQLite uses absolute paths to avoid CWD resolution issues
   - **Error handling**: Try/except blocks with fallbacks throughout
   - **Pagination**: Default 20 items per page, max 100
   - **Batch processing**: Statement transformations process 100 records at a time

---

## Development Setup

### Backend Setup

```bash
# Navigate to backend directory
cd code/AssetManagementAnomalyDetection

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Configure environment (development)
export FLASK_ENV=development
export PORT=5050
export USE_LOCAL_SQLITE=true

# Initialize database (creates tables automatically on first run)
python app.py

# Run the Flask development server
python app.py
# Server runs at http://127.0.0.1:5050
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd code/AssetManagementAnomalyDetection/frontend

# Install dependencies
npm install

# Start development server
npm start
# Proxies API calls to http://127.0.0.1:5050 (see package.json)

# Build for production
npm run build

# Run tests
npm test
```

### Business Analysis Engine

```bash
# Run from project root
python analysis/business_analyzer.py

# Output: analysis/business_analysis_results.json
```

### OCR Processing (Optional)

```bash
# Install system dependencies first
# macOS: brew install poppler tesseract
# Ubuntu: apt-get install poppler-utils tesseract-ocr

# Install Python packages
pip install pdf2image pytesseract Pillow

# Process PDFs
cd code/scripts
python ocr_processor_v3.py --property-dir ../../code/sample-data/rental-statements/property-a --output property-a-tuned.csv
```

### Docker Build & Run

```bash
# Build container
cd code/AssetManagementAnomalyDetection
docker build -t asset-management-app .

# Run locally
docker run -p 5000:5000 \
  -e FLASK_ENV=production \
  -e USE_LOCAL_SQLITE=true \
  asset-management-app
```

### Environment Configuration

#### Development (.env)
```bash
FLASK_ENV=development
PORT=5050
USE_LOCAL_SQLITE=true
DATABASE_URL=sqlite:///instance/asset_management.db  # Optional override
```

#### Production (Azure App Settings)
```bash
FLASK_ENV=production
PORT=5000
AZURE_SQL_SERVER=ocr-backend-sql
AZURE_SQL_DATABASE=OCRDatabase
AZURE_SQL_USERNAME=<username>
AZURE_SQL_PASSWORD=<password>
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=<endpoint>
AZURE_DOCUMENT_INTELLIGENCE_KEY=<key>
```

#### .env File Setup (Development)
```bash
# Copy example to start
cp .env.example .env

# Edit .env with your credentials (NEVER COMMIT THIS FILE)
FLASK_ENV=development
PORT=5050
USE_LOCAL_SQLITE=true

# Azure OCR (Optional - uses local Tesseract if not provided)
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com
AZURE_DOCUMENT_INTELLIGENCE_KEY=your-key-here
```

---

## Database Schema

### Core Tables

#### portfolios
- `id` (Primary Key)
- `name` VARCHAR(100)
- `manager` VARCHAR(100)
- `total_assets` FLOAT
- `created_at` DATETIME

#### assets
- `id` (Primary Key)
- `portfolio_id` (Foreign Key → portfolios)
- `symbol` VARCHAR(10)
- `name` VARCHAR(100)
- `quantity` FLOAT
- `purchase_price` FLOAT
- `current_price` FLOAT (nullable)
- `purchase_date` DATE

#### fees
- `id` (Primary Key)
- `portfolio_id` (Foreign Key → portfolios)
- `amount` FLOAT
- `date` DATE
- `fee_type` VARCHAR(50) (e.g., 'management', 'performance')
- `description` TEXT (nullable)

#### anomalies
- `id` (Primary Key)
- `portfolio_id` (Foreign Key → portfolios)
- `fee_id` (Foreign Key → fees)
- `anomaly_score` FLOAT
- `detected_at` DATETIME
- `reviewed` BOOLEAN (default: False)

#### parsed_statements
- `id` (Primary Key)
- `filename` VARCHAR(255)
- `upload_batch` VARCHAR(100) (timestamp-based)
- `property_id` VARCHAR(255) (nullable)
- `statement_date` VARCHAR(50) (nullable)
- `rent` FLOAT (nullable)
- `management_fee` FLOAT (nullable)
- `repair` FLOAT (nullable)
- `deposit` FLOAT (nullable)
- `misc` FLOAT (nullable)
- `total` FLOAT (nullable)
- `confidence` FLOAT (nullable)
- `processing_method` VARCHAR(50) ('azure' or 'local')
- `uploaded_at` DATETIME
- `raw_text` TEXT (nullable)
- `field_confidences` TEXT (nullable, JSON string)

### Schema Rules & Requirements

**Every table must include:**
```sql
CREATE TABLE example_table (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    -- Business columns here
    -- Metadata (REQUIRED)
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_file_hash VARCHAR(64),  -- For deduplication
    processing_method VARCHAR(50)   -- Track data origin
);
```

**Schema Standards:**
- **Primary keys**: Always `BIGINT`, auto-incrementing
- **Timestamps**: `created_at`, `updated_at` on every table
- **Source metadata**: Track origin (file hash, agent, statement date)
- **Foreign keys**: Always enforced; cascades must be explicit (`ON DELETE CASCADE` vs `ON DELETE RESTRICT`)
- **NOT NULL**: Prefer NOT NULL constraints over nullable + app-level checks
- **Unique constraints**: Apply where logically required (e.g., file hash + date)
- **Indexes**: Justify in migration description and PR; explain in comments

**Alembic Migration Example:**
```python
# Migration file: 20240315_add_parsed_statements_table.py
def upgrade():
    op.create_table(
        'parsed_statement',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('property_id', sa.String(255)),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    # Index justification: Property queries are frequent in analytics
    op.create_index('ix_parsed_statement_property_id', 'parsed_statement', ['property_id'])

def downgrade():
    op.drop_index('ix_parsed_statement_property_id')
    op.drop_table('parsed_statement')
```

### Transaction Safety

**Multi-step writes must be wrapped in transactions:**
```python
from sqlalchemy.orm import Session

def store_parsed_statements(statements: list[dict], session: Session) -> None:
    """Store multiple parsed statements in a transaction."""
    try:
        for stmt_data in statements:
            stmt = ParsedStatement(**stmt_data)
            session.add(stmt)
        session.commit()
        logger.info(f"Stored {len(statements)} statements")
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to store statements: {e}")
        raise
```

**Transaction Rules:**
- **No autocommit**: Explicit commit/rollback only
- **Idempotent operations**: Use `INSERT ... ON CONFLICT` or equivalent for upserts
- **Atomic updates**: Group related changes in single transaction

### Data Lineage

Full traceability from anomaly back to source:
```
anomaly → fee → statement_entry → statement_raw → source PDF filename
```

---

## API Endpoints

### Core API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check/info |
| GET | `/upload` | Serve PDF upload web page |
| GET | `/api/portfolios` | List all portfolios |
| GET | `/api/anomalies/<portfolio_id>` | Get anomalies for a portfolio |
| POST | `/api/detect-anomalies/<portfolio_id>` | Run anomaly detection and persist results |
| POST | `/api/upload-pdf` | Upload single PDF for OCR processing |
| POST | `/api/upload-pdf-batch` | Upload multiple PDFs, store in database |
| GET | `/api/parsed-statements` | Retrieve parsed statement data (paginated) |
| GET | `/api/parsed-statements/summary` | Get aggregated summary of parsed data |
| GET | `/api/statement-raw` | Get raw statement lines (limit parameter) |

### Request/Response Examples

#### Upload Single PDF
```bash
curl -X POST http://127.0.0.1:5050/api/upload-pdf \
  -F "file=@statement.pdf"

# Response
{
  "success": true,
  "data": {
    "rent": 574.39,
    "management_fee": 57.44,
    "repair": 0.0,
    "deposit": 0.0,
    "misc": 0.0,
    "total": 516.95,
    "date": "2023-01-31",
    "property_id": "123 Main St"
  },
  "confidence": 0.92,
  "method": "azure",
  "field_confidences": {...}
}
```

#### Run Anomaly Detection
```bash
curl -X POST http://127.0.0.1:5050/api/detect-anomalies/1

# Response
{
  "message": "Anomaly detection completed",
  "anomalies_found": 3
}
```

### API Design Rules

**RESTful API Principles:**
- **Resource naming**: Plural nouns (`/portfolios`, `/statements`, `/anomalies`)
- **HTTP methods**: GET (read), POST (create), PUT (update/replace), PATCH (partial update), DELETE
- **Pagination**: All list endpoints support `?page=1&per_page=20` (default 20, max 100)
- **Validation**: Use Pydantic or similar for request/response schemas

**Example with Pydantic Validation:**
```python
from flask import request, jsonify
from pydantic import BaseModel, validator

class UploadStatementRequest(BaseModel):
    filename: str
    property_id: str

    @validator('filename')
    def filename_must_be_pdf(cls, v):
        if not v.endswith('.pdf'):
            raise ValueError('must be a PDF file')
        return v

@app.route('/api/statements', methods=['POST'])
def upload_statement():
    try:
        # Validate request
        request_data = UploadStatementRequest(**request.json)

        # Process
        result = process_statement(request_data.filename, request_data.property_id)

        return jsonify({
            "success": True,
            "data": result
        }), 201

    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500
```

**API Contract Rules:**
- **Explicit error shapes**: Always include `success` boolean and `error` message
- **Breaking changes**: Require deprecation notice and version bump (v1 → v2)
- **Response schemas**: Document in OpenAPI/Swagger spec
- **Input validation**: Validate and sanitize all external inputs

---

## Coding Standards

### Language-Specific Formatting

#### Python

- **Style**: Follow PEP 8 with 99-column line limit
- **Formatting**: Black-compatible formatting, isort for imports
- **Import order**: Standard library → third-party → local (each alphabetically sorted)
- **Type hints**: Required on all function signatures; use `mypy --strict` for core modules (ingestion, schema, business logic)
- **Linting**: Code must pass flake8/ruff with zero warnings
- **File organization**: One class per file unless strong cohesion justifies multiple

**Good Example:**
```python
from pathlib import Path
from typing import Optional
import logging

import pandas as pd
from sqlalchemy.orm import Session

from code.AssetManagementAnomalyDetection.models import ParsedStatement

logger = logging.getLogger(__name__)

def parse_statement(
    pdf_path: Path,
    session: Session
) -> Optional[ParsedStatement]:
    """Parse a rental statement PDF and store in database.

    Args:
        pdf_path: Absolute path to PDF file
        session: SQLAlchemy database session

    Returns:
        ParsedStatement object if successful, None if parsing fails

    Raises:
        InvalidStatementLayoutError: If PDF format is unrecognized
        DatabaseError: If database write fails

    Example:
        >>> from pathlib import Path
        >>> stmt = parse_statement(Path("statement.pdf"), db_session)
        >>> print(stmt.rent)
        1234.56
    """
    try:
        # Validate input
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        # Process with OCR
        ocr_processor = get_ocr_processor()
        data = ocr_processor.process_pdf(pdf_path)

        # Store in database (transaction-safe)
        stmt = ParsedStatement(**data)
        session.add(stmt)
        session.commit()

        logger.info(
            "Statement parsed successfully",
            extra={"filename": pdf_path.name, "rent": data.get("rent")}
        )
        return stmt

    except InvalidStatementLayoutError as e:
        logger.error(f"Invalid PDF layout: {e}", extra={"file": pdf_path.name})
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Parse failed: {e}", extra={"file": pdf_path.name})
        return None
```

#### TypeScript/JavaScript

- **Preference**: Always use TypeScript for new code
- **Formatting**: Prettier-compatible
- **Linting**: ESLint with `@typescript-eslint` rules
- **Type safety**: `strict: true` in tsconfig.json, no implicit `any`
- **Exports**: Named exports for utilities, default exports only for React components

**Good Example:**
```typescript
// Good: Explicit types, named exports
export interface StatementData {
  rent: number;
  managementFee: number;
  date: string;
  propertyId: string;
}

export async function fetchStatements(
  portfolioId: number
): Promise<StatementData[]> {
  const response = await axios.get(`/api/statements/${portfolioId}`);
  return response.data;
}

// React component: default export OK
export default function Dashboard() {
  // Component implementation
}
```

#### SQL (PostgreSQL/Azure SQL)

- **Keywords**: UPPERCASE for SQL keywords
- **Identifiers**: lowercase, snake_case for tables and columns
- **Table names**: Singular for entities (use `portfolio`, not `portfolios` unless it's truly a collection)
- **No SELECT \***: Always specify columns in committed code
- **Migrations**: All schema changes via Alembic or equivalent migration tool
- **Documentation**: Document all views/materialized views with owning module

**Good Example:**
```sql
-- Good: Explicit columns, uppercase keywords, clear naming
SELECT
    p.id,
    p.name AS portfolio_name,
    SUM(f.amount) AS total_fees
FROM portfolio p
INNER JOIN fee f ON f.portfolio_id = p.id
WHERE f.date >= '2024-01-01'
GROUP BY p.id, p.name
ORDER BY total_fees DESC;
```

### Naming Conventions

#### General Rules
- **Modules/packages**: `snake_case` (e.g., `ocr_processor`, `business_logic`)
- **Classes**: `PascalCase` (e.g., `ParsedStatement`, `AnomalyDetector`)
- **Functions/methods/variables**: `snake_case` (e.g., `parse_pdf`, `total_amount`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_BATCH_SIZE`, `DEFAULT_PORT`)
- **Test files**: Mirror module name with `_test` suffix (e.g., `azure_processor_test.py`)
- **Migration files**: Sequential ID + short purpose tag (e.g., `20240315_add_parsed_statements_table.py`)

#### Domain Terminology
- **Use stable nouns**: `property`, `statement`, `transaction`, `fee`, `anomaly`
- **Avoid abbreviations**: Except widely recognized (`id`, `url`, `api`, `ocr`, `pdf`)
- **Be explicit**: `management_fee` not `mgmt_fee`, `statement_date` not `stmt_dt`

**Good vs Bad:**
```python
# Good: Clear, descriptive names
class ParsedStatement:
    def calculate_net_amount(self) -> float:
        return self.rent - self.management_fee - self.repair

# Bad: Unclear abbreviations
class PStmt:
    def calc_net_amt(self) -> float:
        return self.rnt - self.mgmt_f - self.rpr
```

### Project Structure & Dependencies

#### Backend Package Organization (Ideal)
```
code/AssetManagementAnomalyDetection/
├── api/              # Flask routes (API layer)
├── business_logic/   # Business rules, calculations, analytics
├── db/               # Database initialization, session management
├── models.py         # SQLAlchemy models
├── ingestion/        # Data ingestion pipelines
├── ocr/              # OCR processing (Azure + local)
├── ml/               # Machine learning modules
├── scripts/          # Utility scripts, migrations
└── utils/            # Pure utility functions
```

**Utilities must be:**
- Pure functions (no side effects) OR
- Clearly documented as side-effecting with explicit documentation

#### Dependency Management
- **Pin exact versions** in `requirements.txt` or `package.json`
- **Use lockfiles**: `requirements.lock` or `package-lock.json`
- **No unused packages**: Remove before committing
- **Security updates**: Review and update within one sprint/iteration

### Error Handling & Reliability

**Good Example:**
```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class InvalidStatementLayoutError(ValueError):
    """Raised when PDF layout is unrecognized."""
    pass

def extract_rent_amount(text: str, property_id: str) -> Optional[float]:
    try:
        # Parse rent from text
        rent = parse_rent_field(text)
        return rent
    except ValueError as e:
        logger.warning(
            "Failed to parse rent amount",
            extra={
                "property_id": property_id,
                "error": str(e),
                "module": __name__
            }
        )
        return None
    except InvalidStatementLayoutError:
        logger.error(
            "Unrecognized statement layout",
            extra={"property_id": property_id}
        )
        raise  # Re-raise for caller to handle
```

**Bad Example:**
```python
# Bad: Bare except, no context
def extract_rent_amount(text):
    try:
        return parse_rent_field(text)
    except:
        return None  # Lost all error information!
```

**Error Handling Rules:**
- **No bare `except`**: Always catch specific exception types
- **Log with context**: Include module, function, entity IDs in structured fields
- **Custom exceptions**: Use for business-rule violations (e.g., `InvalidStatementLayoutError`)
- **Retries**: Use exponential backoff with jitter for network/IO operations
- **Idempotency**: All ingestion steps must be idempotent (re-running cannot duplicate rows)

### Logging & Observability

**Structured Logging:**
```python
import logging
import json

# Configure structured logging
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Good: Structured logging with context
logger.info(
    "Statement parsed successfully",
    extra={
        "property_id": "123-main-st",
        "batch_id": "20240315_143022",
        "rent_amount": 1200.00,
        "processing_method": "azure"
    }
)

# For JSON logging (production):
log_data = {
    "level": "info",
    "message": "Statement parsed successfully",
    "property_id": "123-main-st",
    "batch_id": "20240315_143022"
}
print(json.dumps(log_data))
```

**Log Levels:**
- **DEBUG**: Developer detail, verbose data dumps (not in production)
- **INFO**: Pipeline milestones, successful operations, key metrics
- **WARNING**: Recoverable anomalies, fallback triggered, deprecated usage
- **ERROR**: Failed operations, caught exceptions requiring attention
- **CRITICAL**: System-wide impact, service unavailable, data corruption

**Observability Requirements:**
- **Metrics**: Emit counts for ingestion, parse failures, dedupe events, DB latencies, API response times
- **Tracing**: Propagate request IDs and batch IDs through all layers
- **Structured fields**: Always include `module`, `function`, `entity_id` where applicable

### Documentation Requirements

**Module Documentation:**
```python
"""
OCR Processing Module
=====================

Purpose:
    Extract structured data from rental property statement PDFs using
    Azure Document Intelligence or local Tesseract OCR.

Public Interfaces:
    - get_ocr_processor() -> OCRProcessor
    - AzureOCRProcessor.process_pdf(path: Path) -> dict
    - LocalOCRProcessor.process_pdf(path: Path) -> dict

Invariants:
    - All processors return same output schema (rent, fees, dates)
    - PDF files are never modified, only read
    - Results are cached by file hash to avoid re-processing

Failure Modes:
    - InvalidStatementLayoutError: Unrecognized PDF format
    - AzureAPIError: Azure service unavailable (falls back to local)
    - ProcessingTimeoutError: OCR took >60 seconds

Dependencies:
    - Azure Document Intelligence API (optional)
    - Tesseract OCR (fallback)
    - pdf2image, Pillow
"""
```

**Function Documentation:**
```python
def extract_rent_amount(text: str, property_id: str) -> Optional[float]:
    """
    Extract monthly rent amount from statement text.

    Args:
        text: Raw OCR text from statement PDF
        property_id: Property identifier for logging context

    Returns:
        Rent amount as float, or None if not found

    Raises:
        InvalidStatementLayoutError: If text format is unrecognized

    Example:
        >>> text = "Monthly Rent: $1,234.56"
        >>> extract_rent_amount(text, "prop-123")
        1234.56
    """
```

**Documentation Checklist:**
- [ ] Module-level docstring with purpose, interfaces, invariants, failure modes
- [ ] Function docstrings with Args, Returns, Raises, Examples
- [ ] README for each major package explaining architecture
- [ ] Migration files include rationale and rollback strategy
- [ ] ADRs (Architecture Decision Records) for significant choices

### Git Commit Standards

**Commit Message Format:**
```
<type>(scope): short imperative summary (max 72 chars)

Body explains what and why (not how). Link to issue.
List notable side effects or migrations.

Fixes #123
```

**Types:**
- **feat**: New feature
- **fix**: Bug fix
- **refactor**: Code restructuring without behavior change
- **chore**: Maintenance (dependency updates, config)
- **docs**: Documentation only
- **test**: Test additions or fixes
- **perf**: Performance improvement

**Examples:**
```
feat(ocr): add Azure Document Intelligence fallback

Add automatic fallback to local Tesseract OCR when Azure API
credentials are missing or service is unavailable. This improves
reliability for local development and handles service outages.

- AzureOCRProcessor now catches connection errors
- get_ocr_processor() selects based on credential availability
- Added integration test for fallback scenario

Fixes #45
```

```
fix(api): prevent duplicate statement uploads

Add unique constraint on (file_hash, property_id, statement_date)
to prevent duplicate entries when users re-upload the same PDF.

Migration: 20240315_add_unique_constraint.py (reversible)

Fixes #67
```

### Anti-Patterns to Avoid

**❌ DON'T DO THIS:**

```python
# 1. Bare except
try:
    result = risky_operation()
except:  # Catches everything, hides bugs
    return None

# 2. String-based SQL
query = f"SELECT * FROM users WHERE id = '{user_id}'"  # SQL injection!

# 3. Direct DB from API
@app.route('/users/<id>')
def get_user(id):
    user = db.session.query(User).get(id)  # Skips business logic layer
    return jsonify(user)

# 4. Missing type hints
def calculate_fee(amount):  # No types
    return amount * 0.1

# 5. Abbreviations in names
class PStmt:  # Unclear
    def calc_net_amt(self):
        return self.rnt - self.mgmt_f

# 6. Loading entire file into memory
with open(pdf_path, 'rb') as f:
    entire_pdf = f.read()  # Bad for large files

# 7. N+1 queries
for portfolio in portfolios:
    fees = session.query(Fee).filter_by(portfolio_id=portfolio.id).all()
```

**✅ DO THIS INSTEAD:**
See good examples in sections above.

### Code Quality Targets

When writing or reviewing code, aim for these measurable targets:

- **Test coverage**: ≥80% project-wide, ≥90% for business logic and parsing
- **Cyclomatic complexity**: ≤10 per function (warn 11-20, refactor >20)
- **PR size**: ≤400 lines changed (justify if >800)
- **API latency**: p95 <300ms for reads
- **Build success**: All linters, type checks, tests pass before merge

### Standards Exception Process

If a coding standard must be violated (e.g., emergency hotfix):

**1. Add comment in code:**
```python
# STANDARDS EXCEPTION: Bypassing transaction for emergency data fix
# Ticket: #789 - Will refactor to use proper transaction pattern
# Justification: Need immediate fix for prod data corruption
unsafe_direct_db_update()
```

**2. Include in PR description:**
```markdown
## Standards Exception

**Rule violated**: Transaction safety requirement
**Scope**: Single function in `scripts/emergency_fix.py`
**Justification**: Emergency prod fix, data corruption ongoing
**Follow-up**: #790 - Refactor to use proper transaction pattern (due: next sprint)
```

---

## Testing Requirements

### Testing Philosophy

- **Write tests BEFORE code** (Test-Driven Development)
- **No code without tests** - PRs without tests will be rejected
- **Tests as documentation** - Tests show how code should be used

### Test Pyramid

```
        ┌─────────────┐
        │  E2E Tests  │  ← 5-10% of tests, critical workflows only
        └─────────────┘
       ┌───────────────┐
       │  Integration  │  ← 20-30% of tests, API + DB
       │     Tests     │
       └───────────────┘
    ┌─────────────────────┐
    │    Unit Tests       │  ← 60-75% of tests, business logic
    └─────────────────────┘
```

### Coverage Expectations

- **Minimum project-wide**: 80% line coverage
- **Business logic & parsing**: ≥90% line coverage
- **Critical paths**: ≥90% coverage (security, anomaly detection, payment processing)
- **New code**: All new functions must include tests
- **Bug fixes**: Add regression test for every bug

### Unit Test Examples

```python
import pytest
from code.ocr.azure_processor import extract_rent_amount

def test_extract_rent_amount_valid():
    """Test extracting rent from properly formatted text."""
    text = "Monthly Rent: $1,234.56"
    result = extract_rent_amount(text)
    assert result == 1234.56

def test_extract_rent_amount_missing():
    """Test handling when rent field is missing."""
    text = "No rent information"
    result = extract_rent_amount(text)
    assert result is None

def test_extract_rent_amount_invalid_format():
    """Test handling when rent format is invalid."""
    text = "Monthly Rent: INVALID"
    with pytest.raises(InvalidStatementLayoutError):
        extract_rent_amount(text)
```

### Integration Test Examples

```python
import pytest
from flask import Flask
from code.AssetManagementAnomalyDetection.app import app
from code.AssetManagementAnomalyDetection.db import db

@pytest.fixture
def client():
    """Create test client with temporary database."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_upload_pdf_endpoint(client):
    """Test PDF upload API endpoint."""
    with open('test_statement.pdf', 'rb') as pdf:
        response = client.post('/api/upload-pdf', data={'file': pdf})

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'rent' in data['data']
```

### End-to-End Test Examples

```python
def test_complete_statement_processing_pipeline(client, sample_pdf):
    """
    E2E test: Upload PDF → Parse → Store → Retrieve → Display

    Verifies the complete user workflow from upload to dashboard display.
    """
    # 1. Upload PDF
    response = client.post('/api/upload-pdf-batch', data={'files': [sample_pdf]})
    assert response.status_code == 200
    batch_id = response.get_json()['batch_id']

    # 2. Retrieve parsed data
    response = client.get(f'/api/parsed-statements?batch_id={batch_id}')
    statements = response.get_json()['data']
    assert len(statements) > 0

    # 3. Verify data integrity
    stmt = statements[0]
    assert stmt['rent'] == 1200.00  # Known value from sample_pdf
    assert stmt['property_id'] == '123 Main St'
```

### Test Quality Rules

- **Fail-then-pass**: Write failing test first, then implement feature
- **No flaky tests**: Tests must be deterministic; randomized tests must be seed-locked
- **Mock external dependencies**: Mock Azure APIs, file system, external services
- **Fast execution**: Unit tests should run in milliseconds

### Running Tests

```bash
# Frontend tests
cd code/AssetManagementAnomalyDetection/frontend
npm test

# Backend tests (when implemented)
cd code/AssetManagementAnomalyDetection
pytest

# With coverage
pytest --cov=. --cov-report=html
```

### Manual Testing (Current State)

Until automated tests are fully implemented, test manually via:
- **Backend API**: Use `curl`, Postman, or the built-in `/upload` page (static/upload.html)
- **OCR testing**: Use `code/ocr/test_pdf_upload.html` for interactive testing
- **Frontend testing**: Use `npm start` and navigate to http://localhost:3000
- **Sample data**: Use PDFs in `code/sample-data/rental-statements/` for testing

---

## Security & Secrets

### SQL Injection Prevention (CRITICAL)

**Good: Parameterized query via SQLAlchemy**
```python
from sqlalchemy import text

def get_statements_by_property(property_id: str, session: Session):
    query = text("SELECT * FROM parsed_statement WHERE property_id = :prop_id")
    return session.execute(query, {"prop_id": property_id}).fetchall()
```

**Bad: String concatenation - FORBIDDEN**
```python
def get_statements_by_property(property_id: str, session: Session):
    query = f"SELECT * FROM parsed_statement WHERE property_id = '{property_id}'"
    return session.execute(query).fetchall()  # SQL injection vulnerability!
```

### Security Checklist

- **No secrets in code**: Use `.env` files (ignored by git)
- **Input validation**: Validate and sanitize all external inputs (PDF metadata, form data)
- **Parameterized SQL**: Always use SQLAlchemy ORM or parameterized queries
- **PII masking**: Mask sensitive data in logs (addresses, tenant names, SSN)
- **Dependency scanning**: Review security advisories (use `safety`, `pip-audit`, `npm audit`)
- **CORS configuration**: Restrict allowed origins in production
- **Rate limiting**: Apply to API endpoints to prevent abuse

### Secrets Management

**Never commit secrets to git:**
```bash
# Check if secrets accidentally committed
git log --all --full-history -- .env
git log -S "AZURE_DOCUMENT_INTELLIGENCE_KEY"

# If found, use git-filter-repo or BFG to remove from history
```

**Use .env files (add to .gitignore):**
```bash
# .env.example (committed to repo)
FLASK_ENV=development
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com
AZURE_DOCUMENT_INTELLIGENCE_KEY=your-key-here

# .env (NOT committed, in .gitignore)
FLASK_ENV=production
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://prod-endpoint.cognitiveservices.azure.com
AZURE_DOCUMENT_INTELLIGENCE_KEY=actual-secret-key-abc123
```

**Azure secrets via App Settings (not in code):**
```bash
az webapp config appsettings set \
  --name ocr-backend-app \
  --resource-group asset-management-rg-v2 \
  --settings AZURE_DOCUMENT_INTELLIGENCE_KEY=<secret-value>
```

### Input Validation

- Validate all user inputs at API boundaries
- Sanitize PDF metadata before processing
- Use Pydantic for request validation
- Never trust client-side validation alone

### PII Handling

- **Mask in logs**: addresses, tenant names, property IDs
- **Anonymize in analytics**: aggregate only, no individual data
- **Secure in transit**: HTTPS only in production

---

## Performance Guidelines

### Performance Targets

- **API latency**: p95 < 300ms for standard reads
- **Ingestion throughput**: 100 PDFs/minute (target)
- **Database queries**: Use EXPLAIN ANALYZE to verify indexes

### Performance Rules

- **Stream large files**: Don't load entire PDFs into memory
- **Bulk inserts**: Use `COPY` or `executemany()` for batch operations
- **Always paginate**: List endpoints (default 20, max 100)
- **Lazy load**: Heavy resources (ML models, large files) on-demand
- **O(n²) complexity**: Must be justified and ticketed for optimization if on batch paths

### Performance Anti-Patterns

**❌ DON'T: Load entire PDF into memory**
```python
with open(pdf_path, 'rb') as f:
    entire_pdf = f.read()  # Bad for large files
```

**✅ DO: Stream page by page**
```python
def process_large_pdf(pdf_path: Path) -> Iterator[dict]:
    """Process PDF page-by-page to avoid memory issues."""
    with open(pdf_path, 'rb') as f:
        pdf_reader = PdfReader(f)
        for page in pdf_reader.pages:
            yield extract_page_data(page)
```

**❌ DON'T: N+1 queries**
```python
for portfolio in portfolios:
    fees = session.query(Fee).filter_by(portfolio_id=portfolio.id).all()
```

**✅ DO: Eager loading**
```python
from sqlalchemy.orm import joinedload

portfolios = session.query(Portfolio).options(joinedload(Portfolio.fees)).all()
```

**✅ DO: Bulk database insert**
```python
def bulk_insert_statements(statements: list[dict], session: Session):
    """Insert multiple statements efficiently."""
    session.bulk_insert_mappings(ParsedStatement, statements)
    session.commit()
```

### Monitoring

- Log slow queries (>100ms)
- Track API endpoint latencies
- Monitor OCR processing times
- Alert on anomaly detection failures

---

## Code Review Checklist

### Pull Request Guidelines

#### PR Size & Scope

- **Target**: ≤ 400 lines of code (LOC) changed
- **Maximum**: 800 LOC; must include rationale and review plan if exceeded
- **Focus**: One feature or bug fix per PR; avoid mixing unrelated changes
- **Breaking changes**: Separate PR with detailed migration guide

#### PR Description Template

```markdown
## Why
[Explain the problem being solved or feature being added]

## What
[Summarize the changes made]

## How Tested
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing steps: [describe]
- [ ] Screenshots/logs attached (for UI/performance changes)

## Risks
[Potential issues, edge cases, or areas needing extra attention]

## Rollback Plan
[How to revert this change if needed]

## Database Changes
- [ ] No schema changes
- [ ] Schema migration included (forward + backward)
- [ ] Data backfill script provided
- [ ] Migration tested on staging

## API Changes
- [ ] No API changes
- [ ] OpenAPI spec updated
- [ ] Breaking changes documented
- [ ] Backward compatibility maintained
```

#### Risky PR Criteria (Requires Extra Scrutiny)

Flag PRs as "risky" if they involve:
- **Database schema changes**: Migrations, new tables, column modifications
- **Authentication/authorization**: Login, permissions, access control
- **Core parsing logic**: OCR processing, fee extraction, data transformation
- **ML model changes**: Algorithm updates, feature engineering, model retraining
- **Security-sensitive code**: Payment processing, PII handling, encryption
- **Public API changes**: Breaking changes, new endpoints, contract modifications
- **Infrastructure**: Deployment configuration, database connection, Azure services

Risky PRs should:
- Include detailed testing plan
- Have synchronous review session if needed
- Update relevant runbooks and documentation
- Include rollback procedure

### Review Checklist

**Design & Architecture**
- [ ] Follows API → business_logic → db layering
- [ ] No forbidden imports or circular dependencies
- [ ] Module responsibilities are clear and focused
- [ ] Reuses existing utilities rather than duplicating code

**Correctness**
- [ ] Input validation covers edge cases
- [ ] Error handling is comprehensive
- [ ] Business logic matches requirements
- [ ] Database operations are transaction-safe

**Tests**
- [ ] Unit tests fail without the code changes
- [ ] Integration tests cover happy path and error cases
- [ ] Test coverage meets thresholds (≥80%)
- [ ] E2E tests added for critical workflows

**Security & Privacy**
- [ ] No SQL injection vulnerabilities (parameterized queries)
- [ ] Authorization checks present
- [ ] PII masked in logs and error messages
- [ ] No secrets in code or commit history
- [ ] Dependencies reviewed for known vulnerabilities

**Performance**
- [ ] Database queries are indexed or justified
- [ ] No N+1 query issues
- [ ] Expensive operations are paginated/batched
- [ ] Caching considered for repeated operations

**Observability**
- [ ] Structured logging added for key operations
- [ ] Error logs include sufficient context
- [ ] Metrics/traces added for performance monitoring
- [ ] Alerts updated if adding critical functionality

**Documentation**
- [ ] Code comments explain "why" not "what"
- [ ] Docstrings added for public functions
- [ ] README updated for new features
- [ ] OpenAPI spec updated for API changes
- [ ] Migration notes included for database changes
- [ ] CLAUDE.md updated if architecture changes

**Deployment & Rollout**
- [ ] Feature flag or safe-by-default behavior
- [ ] Rollback path clearly described
- [ ] Migration tested (forward and backward)
- [ ] Deployment runbook updated

### Code Review Process

#### Standard PRs
- **Human reviewers**: ≥ 1 required
- **AI reviewers**: 1 Claude Code review recommended
- **Approval**: At least 1 human approval required
- **Merge blockers**: Failing tests, unresolved review comments, missing documentation

#### Risky PRs
- **Human reviewers**: 2 required (including code owner)
- **AI reviewers**: 2 Claude Code reviews with different prompts/focus areas
- **Synchronous review**: Schedule live review session if no decision within 72h
- **Additional checks**: Migration dry-run, security scan, performance testing

#### Merge Blockers (Gates)
- [ ] All CI checks pass (lint, type check, tests, coverage, security scans)
- [ ] Required reviewers approved (no unresolved "request changes")
- [ ] OpenAPI/spec updated if API changed
- [ ] Database migrations included and tested (forward + backward)
- [ ] No secrets detected in diff (manual or automated scan)
- [ ] Documentation updated (README, CLAUDE.md, runbooks)

#### Merge Strategy
- **Default**: Squash-merge to keep main branch history clean
- **Alternative**: Rebase-merge allowed for preserving detailed commit history
- **Protected branch**: `main` requires PR reviews, no direct pushes
- **Post-merge**: Auto-close linked issues, delete merged branches

---

## Deployment & Azure

### Azure Environment (Production)

#### Fixed Configuration Values

**⚠️ NEVER CHANGE THESE - Hardcoded in Azure:**

```bash
RESOURCE_GROUP="asset-management-rg-v2"
APP_NAME="ocr-backend-app"
ACR_NAME="assetmgmtsuiacr"
ACR_LOGIN_SERVER="assetmgmtsuiacr.azurecr.io"
DB_SERVER="ocr-backend-sql"
DB_NAME="OCRDatabase"
REGION="centralus"
SKU="B1"  # Basic tier
```

#### Azure SQL Database
- **Server**: ocr-backend-sql
- **Database**: OCRDatabase
- **Authentication**: SQL Authentication
- **Credentials**: Stored in Azure App Settings (never in code)
- **Connection**: Auto-resolved via environment variables in production

#### Container Registry (ACR)
- **Registry**: assetmgmtsuiacr.azurecr.io
- **Image naming**: `assetmgmtsuiacr.azurecr.io/<image-name>:<tag>`
- **Authentication**: Azure CLI login

### Deployment Workflow

#### Step-by-Step Deployment (SAFE)

```bash
# 1. Verify you're in the right directory
cd code/AssetManagementAnomalyDetection
pwd  # Should show: .../code/AssetManagementAnomalyDetection

# 2. Build Docker image (ARM64 hosts: add --platform flag)
docker build --platform linux/amd64 -t assetmgmtsuiacr.azurecr.io/ocr-backend:$(date +%Y%m%d-%H%M%S) .

# 3. Test image locally BEFORE pushing
docker run -p 5000:5000 \
  -e FLASK_ENV=development \
  -e USE_LOCAL_SQLITE=true \
  assetmgmtsuiacr.azurecr.io/ocr-backend:<your-tag>

# Test: curl http://localhost:5000/
# Expected: {"status": "ok", ...}

# 4. Login to ACR
az login
az acr login --name assetmgmtsuiacr

# 5. Push to ACR
docker push assetmgmtsuiacr.azurecr.io/ocr-backend:<your-tag>

# 6. Verify image in ACR
az acr repository show-tags --name assetmgmtsuiacr --repository ocr-backend --orderby time_desc

# 7. Deploy to App Service
az webapp config container set \
  --name ocr-backend-app \
  --resource-group asset-management-rg-v2 \
  --docker-custom-image-name assetmgmtsuiacr.azurecr.io/ocr-backend:<your-tag>

# 8. Restart App Service
az webapp restart --name ocr-backend-app --resource-group asset-management-rg-v2

# 9. Monitor deployment
az webapp log tail --name ocr-backend-app --resource-group asset-management-rg-v2

# 10. Verify production
curl https://ocr-backend-app.azurewebsites.net/
```

#### Automated Deployment Script

```bash
# Use existing script (with caution)
cd code/AssetManagementAnomalyDetection
chmod +x azure-deployment/deploy.sh
./azure-deployment/deploy.sh

# ALWAYS review script before running
# ALWAYS test locally first
```

### Common Deployment Issues

#### Issue 1: Image Build Fails on ARM64 (M1/M2/M3/M4 Mac)

**Symptom:** Image fails to run on Azure with "exec format error"

**Solution:**
```bash
docker build --platform linux/amd64 -t <image-name> .
```

#### Issue 2: ACR Authentication Fails

**Symptom:** "unauthorized: authentication required"

**Solution:**
```bash
az login
az acr login --name assetmgmtsuiacr
```

#### Issue 3: App Service Shows Old Version

**Symptom:** Deployment succeeded but app shows old code

**Solution:**
```bash
# Restart App Service
az webapp restart --name ocr-backend-app --resource-group asset-management-rg-v2

# Check logs
az webapp log tail --name ocr-backend-app --resource-group asset-management-rg-v2
```

#### Issue 4: Database Connection Fails

**Symptom:** 500 errors, logs show "Cannot connect to database"

**Solution:**
```bash
# Verify App Settings have correct DB credentials
az webapp config appsettings list \
  --name ocr-backend-app \
  --resource-group asset-management-rg-v2 \
  | grep -i sql

# If missing, add:
az webapp config appsettings set \
  --name ocr-backend-app \
  --resource-group asset-management-rg-v2 \
  --settings AZURE_SQL_SERVER=ocr-backend-sql \
              AZURE_SQL_DATABASE=OCRDatabase \
              AZURE_SQL_USERNAME=<username> \
              AZURE_SQL_PASSWORD=<password>
```

### Rollback Procedure

**If deployment breaks production:**

```bash
# 1. Find last working image tag
az acr repository show-tags \
  --name assetmgmtsuiacr \
  --repository ocr-backend \
  --orderby time_desc \
  | head -10

# 2. Deploy previous working tag
az webapp config container set \
  --name ocr-backend-app \
  --resource-group asset-management-rg-v2 \
  --docker-custom-image-name assetmgmtsuiacr.azurecr.io/ocr-backend:<previous-working-tag>

# 3. Restart
az webapp restart --name ocr-backend-app --resource-group asset-management-rg-v2

# 4. Verify
curl https://ocr-backend-app.azurewebsites.net/

# 5. Monitor logs
az webapp log tail --name ocr-backend-app --resource-group asset-management-rg-v2
```

### Docker Configuration

- **Base image**: Python 3.9-slim
- **Includes**: Microsoft ODBC Driver 17 for SQL Server
- **Startup**: Gunicorn with 600s timeout
- **Port**: 5000 (production), 5050 (development)

### Local Development Environment Notes

- **Platform**: ARM64 (M-series Mac) builds require `--platform linux/amd64`
- **Docker**: Version 28.4.0+
- **Azure CLI**: Version 2.77.0+

---

## Troubleshooting

### Backend Won't Start

**Problem:** `python app.py` fails

**Common causes:**
```bash
# 1. Check port 5050 is available
lsof -i :5050
# If in use: kill <PID> or change PORT env var

# 2. Check database connection
export USE_LOCAL_SQLITE=true  # Force local DB

# 3. Check dependencies
pip install -r requirements.txt
```

### Frontend Won't Proxy to Backend

**Problem:** API calls fail with CORS or network errors

**Solution:**
```bash
# 1. Verify backend is running on :5050
curl http://127.0.0.1:5050/

# 2. Check frontend package.json has proxy
cat package.json | grep proxy
# Should show: "proxy": "http://127.0.0.1:5050"

# 3. Restart frontend
npm start
```

### OCR Processing Fails

**Problem:** PDF upload returns errors

**Check:**
```bash
# 1. Are Azure credentials set?
echo $AZURE_DOCUMENT_INTELLIGENCE_KEY
# If empty, OCR falls back to local Tesseract

# 2. Is Tesseract installed? (fallback)
tesseract --version
# If not: brew install tesseract (macOS)

# 3. Check logs for errors
# Look for "InvalidStatementLayoutError" or "ProcessingTimeoutError"
```

### Anomaly Detection Not Working

**Problem:** `/api/detect-anomalies/<id>` returns errors

**Check:**
```bash
# 1. Does ML model exist?
ls code/AssetManagementAnomalyDetection/ml/anomaly_model.pkl

# 2. Are there fees for this portfolio?
# Model needs data to analyze

# 3. Check logs for "Model not found" or training errors
```

### Azure Deployment Issues

**See "Deployment & Azure" section above for detailed troubleshooting**

---

## Additional Resources

### Team Members
- Ming Leong Tsui Lucas
- Xinyu Wang (Iris)
- Xinwen Fang (Sean)
- Zihan Wang
- Boya Zhao
- Sujan Gowda (SJ)

### Additional Documentation
- **Main README**: `README.md`
- **Analysis README**: `analysis/README.md`
- **Product Requirements**: `PRD.md`
- **Azure Deployment Guide**: `code/AssetManagementAnomalyDetection/azure-deployment/AZURE_DEPLOYMENT_GUIDE.md`
- **Team Info**: `TEAM.md`

### External Resources
- **Flask Documentation**: https://flask.palletsprojects.com/
- **SQLAlchemy ORM**: https://docs.sqlalchemy.org/
- **React TypeScript**: https://react-typescript-cheatsheet.netlify.app/
- **Azure Document Intelligence**: https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/
- **Azure App Service**: https://learn.microsoft.com/en-us/azure/app-service/
