## Asset Management Anomaly Detection — Local and Cloud Guide

This directory contains the working sample app (backend + frontend) and supporting scripts. It runs locally with SQLite and can connect to Azure SQL for cloud scenarios.

### Directory structure
- `AssetManagementAnomalyDetection/`
  - `app.py` Flask API (SQLAlchemy models in `models.py`)
  - `frontend/` React TypeScript UI (Create React App)
  - `ml/` Isolation Forest model and inference
  - `scripts/` helper scripts (e.g. CSV upload to Azure SQL)
  - `instance/asset_management.db` local SQLite DB
- `AzureFunctionsApi/` (serverless REST layer; optional, not needed for local run)
- `statement-data.csv` raw statement lines used by the CSV uploader

### Prerequisites
- Python 3.9+ (3.13 tested)
- Node.js 16+ (for the frontend dev server)
- Optional (only if connecting to Azure SQL from your Mac): Microsoft ODBC Driver 17 + `pyodbc`

### 1) Run the backend locally (SQLite)
From the repo root:

```bash
# Ensure local SQLite is used and no external DATABASE_URL overrides it
USE_LOCAL_SQLITE=true FLASK_ENV=development PORT=5050 DATABASE_URL= \
  /usr/local/bin/python3 code/AssetManagementAnomalyDetection/app.py
```

You should see logs like:
- "Using local SQLite (dev): sqlite:///.../instance/asset_management.db"
- "Database tables created successfully"
- Running on http://127.0.0.1:5050

Verify endpoints:
```bash
curl -s http://127.0.0.1:5050/
curl -s http://127.0.0.1:5050/api/portfolios
```

### 2) Seed sample data (SQLite)
```bash
USE_LOCAL_SQLITE=true FLASK_ENV=development DATABASE_URL= \
  /usr/local/bin/python3 code/AssetManagementAnomalyDetection/sample_data.py
```

Re-check portfolios:
```bash
curl -s http://127.0.0.1:5050/api/portfolios
```

### 3) Run the frontend locally (Create React App)
```bash
cd code/AssetManagementAnomalyDetection/frontend
npm install
npm start
```

Open the app at http://localhost:3000. The frontend proxies API calls to `http://127.0.0.1:5050` (configured by `proxy` in `package.json`).

### 4) Upload the CSV into Azure SQL (optional)
The uploader reads `code/statement-data.csv` and writes to Azure table `dbo.statement_raw`.

```bash
AZURE_SQL_SERVER=asset-management-sql \
AZURE_SQL_DATABASE=AssetManagementDB \
AZURE_SQL_USERNAME=sqladmin \
AZURE_SQL_PASSWORD='YOUR_PASSWORD' \
  /usr/local/bin/python3 code/AssetManagementAnomalyDetection/scripts/upload_statement_raw.py
```

If your local backend is running against Azure SQL, you can then GET a sample via:
```bash
curl -s "http://127.0.0.1:5050/api/statement-raw?limit=5"
```

### 5) Connect backend to Azure SQL instead of SQLite (optional)
Install ODBC Driver 17 and ensure `pyodbc` is available. Then start the backend with Azure env vars and without `USE_LOCAL_SQLITE`:

```bash
AZURE_SQL_SERVER=asset-management-sql \
AZURE_SQL_DATABASE=AssetManagementDB \
AZURE_SQL_USERNAME=sqladmin \
AZURE_SQL_PASSWORD='YOUR_PASSWORD' \
FLASK_ENV=production PORT=5050 \
  /usr/local/bin/python3 code/AssetManagementAnomalyDetection/app.py
```

Expected log line: "Using Azure SQL via pyodbc (prod)".

### 6) Live Azure App Service (already deployed)
- Health: `https://asset-management-api-v2.azurewebsites.net/`
- Portfolios: `https://asset-management-api-v2.azurewebsites.net/api/portfolios`
- Statement raw: `https://asset-management-api-v2.azurewebsites.net/api/statement-raw?limit=5`

### Troubleshooting
- Port already in use
  ```bash
  lsof -nP -iTCP:5050 -sTCP:LISTEN -t | xargs -r kill -9
  lsof -nP -iTCP:3000 -sTCP:LISTEN -t | xargs -r kill -9
  ```
- Hitting Azure instead of SQLite locally
  - Ensure `DATABASE_URL` is empty and `USE_LOCAL_SQLITE=true` when running locally.
- Frontend cannot reach API
  - Confirm backend is on 5050 and CRA dev server is on 3000; the frontend `package.json` has `"proxy": "http://127.0.0.1:5050"`.

### Quick commands (copy/paste)
Run backend (SQLite):
```bash
USE_LOCAL_SQLITE=true FLASK_ENV=development PORT=5050 DATABASE_URL= \
  /usr/local/bin/python3 code/AssetManagementAnomalyDetection/app.py
```

Seed data:
```bash
USE_LOCAL_SQLITE=true FLASK_ENV=development DATABASE_URL= \
  /usr/local/bin/python3 code/AssetManagementAnomalyDetection/sample_data.py
```

Run frontend:
```bash
cd code/AssetManagementAnomalyDetection/frontend && npm install && npm start
```
