## Asset Management Anomaly Detection – Monorepo

This project is an end-to-end data pipeline that ingest transactional data in the form of pdf statements with multiple layouts to generate business insights and visually present them. This repo contains:
- A Flask backend with SQLAlchemy and a simple anomaly detection pipeline
- A React TypeScript frontend (Material UI + Chart.js)
- Optional OCR utilities and a deterministic business analysis module

### Repository structure
- `AssetManagementAnomalyDetection/` – Main web app
  - `app.py` – Flask API entrypoint
  - `models.py`, `db.py` – SQLAlchemy models and DB setup
  - `ml/` – ML artifacts (e.g., `anomaly_model.pkl`) and logic
  - `frontend/` – React app (TypeScript, MUI, Chart.js)
  - `instance/asset_management.db` – Default SQLite database (dev)
  - `requirements.txt` – Python dependencies
- `analysis/` – Deterministic KPI analytics (`business_analyzer.py`)
- `code/scripts/` – Optional OCR processors for rental statements

---

## Prerequisites
- Python 3.9+
- Node.js 18+ and npm
- macOS/Linux/Windows supported (commands below shown for macOS/Linux)

Optional (only if you’ll run the OCR scripts in `code/scripts/`):
- Poppler tools (`pdftotext`, `pdftoppm`)
- Tesseract OCR

---

## Backend (Flask) – Setup & Run
1) Create and activate a virtual environment
```bash
cd AssetManagementAnomalyDetection
python3 -m venv .venv
source .venv/bin/activate
```

2) Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3) Configure environment (dev)
```bash
export FLASK_ENV=development
# Port 5001 matches the frontend proxy setting; change if you update the proxy
export PORT=5001
# Set USE_LOCAL_SQLITE to force SQLite in dev (default is already SQLite when FLASK_ENV!=production)
export USE_LOCAL_SQLITE=true
```

4) Initialize the database (SQLite in dev)
```bash
python app.py  # first run will create tables under instance/asset_management.db
```

5) Run the API server
```bash
python app.py
# API runs at http://127.0.0.1:5001 by default (using PORT above)
```

Notes
- For production with Azure SQL, set the following and deploy:
  - `AZURE_SQL_SERVER`, `AZURE_SQL_DATABASE`, `AZURE_SQL_USERNAME`, `AZURE_SQL_PASSWORD`
  - Backend will try pyodbc; if unavailable, it falls back to SQLite
- You can also set `DATABASE_URL` to override DB URI directly

---

## Frontend (React) – Setup & Run
1) Install dependencies
```bash
cd AssetManagementAnomalyDetection/frontend
npm install
```

2) Start the development server
```bash
npm start
```

The frontend proxies API calls to `http://127.0.0.1:5001` (see `frontend/package.json`). If your backend runs on a different port, either:
- Set `PORT` for the backend to match the proxy, or
- Update the `proxy` field in `frontend/package.json` and restart `npm start`.

---

## API Endpoints (summary)
- `GET /` – Health/info
- `GET /api/portfolios` – List portfolios
- `GET /api/anomalies/<portfolio_id>` – List anomalies for a portfolio
- `POST /api/detect-anomalies/<portfolio_id>` – Run anomaly detection and persist results

---

## Optional: OCR utilities (statement parsing)
Scripts under `code/scripts/` can parse rental statements from PDFs.

Python packages (install into your active venv):
```bash
pip install pdf2image pytesseract Pillow
```

System tools:
- Poppler (provides `pdftotext`, `pdftoppm`)
- Tesseract OCR

Example usage:
```bash
cd code/scripts
python ocr_processor_v3.py --property-dir ../../code/sample-data/rental-statements/property-a --output property-a-tuned.csv
```

---

## Optional: Deterministic business analysis
`analysis/business_analyzer.py` computes property/portfolio KPIs from a labeled CSV.

Example:
```bash
python analysis/business_analyzer.py
```
Outputs summarized metrics and writes `analysis/business_analysis_results.json`.

---

## Troubleshooting
- Port mismatch: If the frontend can’t reach the backend, align backend `PORT` with the frontend proxy.
- Database:
  - Dev uses SQLite at `AssetManagementAnomalyDetection/instance/asset_management.db`.
  - To use a different DB, set `DATABASE_URL` or Azure SQL env vars.
- OCR errors:
  - Ensure Poppler/Tesseract are installed and on PATH.
  - Ensure `pdf2image`, `pytesseract`, and `Pillow` are installed in your Python env.
- `psycopg2-binary` errors:
  - Prefer the prebuilt wheel; if building from source, ensure PostgreSQL client tools and `pg_config` are available.

---

## License and contributors
See `LICENSE.txt` and `TEAM.md` for license and team members.