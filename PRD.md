# PRD: Asset Management Anomaly Detection Platform
**Version 2.0** - Updated with implementation decisions

## Summary
An end-to-end system that ingests heterogeneous financial statements (PDF/CSV), performs OCR and parsing, normalizes data to a common schema, transforms entries into fees, and detects anomalous fees per portfolio. It provides a web UI and APIs for uploading statements, exploring portfolios, reviewing anomalies, and exporting reports. Backend runs in Azure App Service (container) with Azure SQL Database. Frontend deployed as Azure Static Web App.

## Goals
- Reduce manual reconciliation of property rental statements by automated ingestion and normalization.
- Detect fee anomalies reliably with transparent data lineage.
- Provide simple dashboards and review workflows for analysts and portfolio managers.
- Enable portfolio performance comparison and hold/sell/acquire recommendations based on real estate metrics (ROI, occupancy, cap rate).

## Non-Goals
- Full-featured document management or enterprise ETL orchestration.
- Real-time streaming ingestion; batch and on-demand are in scope.
- Complex authentication systems beyond OAuth2/JWT.

## Users
- Portfolio Managers: monitor KPIs and anomalies.
- Analysts: upload/parse statements, triage anomalies, export data.
- Admins: manage portfolios, settings, model retraining.

## Environment Context (Azure)
- App URL: https://ocr-backend-app.azurewebsites.net
- Deployment: Azure App Service (Linux) running a Docker container from ACR
- Registry: `assetmgmtsuiacr.azurecr.io`
- Resource Group: `asset-management-rg-v2`
- Region: Central US, SKU: B1 (Basic)
- Database: Azure SQL Database — Server: `ocr-backend-sql`, DB: `OCRDatabase`, SQL Auth (creds in App Settings/.env)
- Local dev: macOS (ARM64), Docker 28.4.0, Azure CLI 2.77.0

## Scope & User Journeys
- Statement ingestion: users upload PDF/CSV → OCR/parse → `statement_raw` + `statement_entries`.
- Transform: map entries → `fees` (date, amount, type, description) per portfolio.
- Anomaly detect: run per portfolio via Isolation Forest → persist to `anomalies`.
- Review: view anomalies, filter/sort, mark reviewed/dismissed, export.
- Dashboard: portfolio list, KPIs, trends, recent anomalies.

## Functional Requirements
- Ingestion
  - Upload PDF/CSV up to 10 MB via UI/API; show progress and errors.
  - Store raw text lines in `statement_raw`; parsed records in `statement_entries`.
  - OCR currently supports one layout (property rental statements); expandable to multiple layouts via rule-based mappers.
  - PDF transforms to schema: property_name, statement_date, period_start, period_end, rent, management_fee, repair, deposit, misc, notes, total, payment_date (aligned with statement_entries table).
- Transformation
  - Batch transform `statement_entries` → `fees` with field mapping (rent→rental_income, management_fee→mgmt_fee, repair→maintenance, etc.).
  - Process in batches of 100 records for optimal performance.
  - Idempotency: avoid duplicates using composite key (portfolio_id, date, fee_type).
- Analytics
  - Detect anomalies per portfolio using Isolation Forest; persist `anomaly_score`, timestamp, link to fee and lineage.
  - Manager comparison: calculate fee efficiency ratio (fees/revenue) per manager.
  - Portfolio performance metrics: ROI, occupancy rate, net operating income (NOI), cap rate.
  - Property-level analysis: rent vs market rate, maintenance costs, vacancy periods.
  - Retrain endpoint with recent data; persist model artifact.
- Data management
  - Full CRUD for `portfolios` and `properties`; read-only for `fees`, `anomalies`.
  - Data lineage: anomaly → fee → entry → raw line → source file metadata.
- Reporting
  - Export CSV for fees and anomalies; summary charts (trends, top anomalies).
  - Manager comparison dashboard showing fee efficiency rankings.
  - Property performance reports with ROI, occupancy, and maintenance costs.
  - Portfolio recommendations: hold/sell/acquire based on performance metrics and market conditions.
- Security & Governance
  - OAuth2 authentication with JWT tokens (Flask-JWT-Extended).
  - CORS restricted to Static Web App domain; inputs validated; secrets in App Settings.

## Non-Functional Requirements
- Availability: 99.5% monthly for API; graceful degradation on OCR heavy tasks.
- Performance (B1):
  - p95 GET endpoints < 200 ms for small payloads.
  - Detect anomalies for ≤ 5k fees within 1–2 s.
  - OCR jobs should complete within 30 s per 10-page PDF (move async if exceeded).
- Scalability: stateless containers; scale out B1→S plans; database tuned with indexes.
- Observability: request logs, error logs, basic metrics; Application Insights optional.

## System Architecture
- Frontend: React (TypeScript, MUI) deployed to Azure Static Web Apps.
- Backend API: Flask app (`code/AssetManagementAnomalyDetection/app.py`) + SQLAlchemy.
- OCR/Parsing: Python utilities (pdf2image/poppler, tesseract) in `ocr/` module (implemented for one layout).
- ML: Isolation Forest model & utilities in `ml/` (`predict.py`, `anomaly_model.pkl`).
- Database: Azure SQL (`portfolios`, `properties`, `fees`, `anomalies`, `statement_raw`, `statement_entries`, `managers`, `users`).
- Authentication: OAuth2 with JWT tokens (Flask-JWT-Extended).
- Async Processing: Celery with Redis for OCR jobs > 30s (recommended for PDFs > 10 pages).

## Data Model (Core Tables)
- users(id, username, email, password_hash, role, created_at, last_login, is_active) -- role: admin, analyst, manager
- managers(id, name, email, phone, efficiency_ratio, total_revenue, total_fees, portfolios_count, created_at, updated_at)
- portfolios(id, name, manager_id, total_value, property_count, created_at, updated_at) -- manager_id FK to managers.id
- properties(id, portfolio_id, name, address, purchase_date, purchase_price, current_value, monthly_rent, market_rate_rent, annual_insurance, annual_property_tax, last_market_update, status) -- status: occupied, vacant, maintenance; NOTE: 1 property = 1 rentable unit
- fees(id, portfolio_id, property_id, amount, date, fee_type, description) -- fee_type: rental_income, mgmt_fee, maintenance, misc
- anomalies(id, portfolio_id, fee_id, anomaly_score, detected_at, reviewed)
- statement_raw(id, line)
- statement_entries(id, source_row_id, portfolio_id, property_id, statement_date, period_start, period_end, rent, management_fee, repair, deposit, misc, notes, total, payment_date, raw_csv) -- source_row_id: FK to first line of entry in statement_raw; property_id: FK to properties.id
- jobs(id, job_type, status, user_id, created_at, started_at, completed_at, progress, result_data, error_message) -- job_type: ocr, transform, performance_calc; status: pending, processing, completed, failed

## API Specification
- Authentication
  - POST `/api/auth/login` → JWT token (OAuth2 flow)
  - POST `/api/auth/refresh` → refresh JWT token
  - GET `/api/auth/user` → current user info (requires JWT)
- Admin (requires admin role)
  - POST `/api/admin/users` → create new user with username, email, password, role
  - GET `/api/admin/users` → list all users
  - PUT `/api/admin/users/{id}` → update user (role, active status)
  - DELETE `/api/admin/users/{id}` → deactivate user
- Health
  - GET `/` → `{ message }` (no auth)
- Portfolio & Data (requires JWT)
  - GET `/api/portfolios` → list of portfolios
  - GET `/api/anomalies/{portfolio_id}` → list of anomalies
  - POST `/api/detect-anomalies/{portfolio_id}` → run detection; returns count
  - GET `/api/statement-raw?limit=n` → raw lines (bounded 1–100)
- Ingestion & Transform (requires JWT)
  - POST `/api/upload-pdf` → upload PDF, trigger OCR (implemented in feat/OCR-backend branch)
  - POST `/api/upload-statement` (multipart) → stores file, OCR/parse, populate raw/entries
  - POST `/api/ingest-entries` → batch transform entries to fees (100 records/batch)
  - POST `/api/retrain-model` → retrains model; returns version info
- Property & Portfolio Analytics (requires JWT)
  - GET `/api/properties` → list all properties across portfolios
  - GET `/api/properties/{id}` → get property details with financial history
  - GET `/api/portfolio/{id}/performance` → calculate portfolio ROI and occupancy metrics
  - GET `/api/managers/comparison` → fee efficiency comparison across managers
  - GET `/api/portfolio/{id}/recommendation` → hold/sell/acquire recommendations based on performance
- Async Job Management (requires JWT)
  - GET `/api/jobs/{job_id}` → get job status and result (returns: id, status, progress, created_at, completed_at, result_data, error_message)
  - GET `/api/jobs?user_id={id}&status={status}` → list jobs with filters
  - DELETE `/api/jobs/{job_id}` → cancel pending job

Request/response schemas follow JSON with error objects `{ error, details }`. All protected endpoints require `Authorization: Bearer <token>` header.

## Frontend Features
- **Authentication Flow:**
  - Login page: username/password form → POST to `/api/auth/login`
  - Store JWT token in localStorage as `access_token`
  - Axios interceptor to add `Authorization: Bearer <token>` header
  - Token refresh: on 401 response, call `/api/auth/refresh` with refresh token
  - Logout: clear localStorage and redirect to login
  - Protected routes: wrap components with `AuthGuard` HOC that checks token validity
  - Implementation:
    ```typescript
    // services/auth.ts
    const authService = {
      login: async (username, password) => {
        const { data } = await axios.post('/api/auth/login', { username, password });
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
      },
      refresh: async () => {
        const refresh = localStorage.getItem('refresh_token');
        const { data } = await axios.post('/api/auth/refresh', { refresh_token: refresh });
        localStorage.setItem('access_token', data.access_token);
      },
      logout: () => {
        localStorage.clear();
        window.location.href = '/login';
      }
    }
    ```
- Upload page: drag-and-drop PDF/CSV, progress, parse summary, error list.
- Dashboard: portfolios with AUM, trends, recent anomalies, quick actions.
- Anomalies: sortable/filterable table, detail drawer (lineage, history), review actions.
- Fees: trend chart, table with filters, export CSV.
- Settings: thresholds, CORS origins, model retrain, portfolio config.

## Settings & Configuration
- Environment variables (App Service container):
  - `WEBSITES_PORT=5000`
  - `FLASK_ENV=production`
  - `AZURE_SQL_SERVER=ocr-backend-sql`
  - `AZURE_SQL_DATABASE=OCRDatabase`
  - `AZURE_SQL_USERNAME` / `AZURE_SQL_PASSWORD`
  - `CORS_ORIGINS=https://<frontend-domain>`
  - Optional: `USE_LOCAL_SQLITE=0/1`, `DATABASE_URL`, `ODBC_DRIVER_NAME` (e.g., "ODBC Driver 18 for SQL Server")
- Local dev: `.env` with the above; `USE_LOCAL_SQLITE=1` preferred.

## Implementation Plan (Milestones)

### Iteration 1: Foundation (Complete)
- ✅ Database models and basic CRUD
- ✅ OCR for single layout PDFs (implemented in feat/OCR-backend branch, pending merge to main)
- ✅ Anomaly detection with Isolation Forest
- ✅ Basic API endpoints
- ✅ Azure deployment

### Iteration 2: Authentication & Analytics (In Progress)
1) OAuth2/JWT Authentication (Self-Hosted)
   - Install Flask-JWT-Extended
   - Implement self-hosted OAuth2 with username/password authentication
   - User credentials stored in database with bcrypt-hashed passwords
   - Login endpoint: POST /api/auth/login (returns JWT token)
   - Refresh endpoint: POST /api/auth/refresh (refreshes expired token)
   - User profile endpoint: GET /api/auth/user (returns current user info)
   - Protect all data endpoints with JWT validation
   - JWT configuration:
     - Access token expiry: 1 hour
     - Refresh token expiry: 7 days
     - Secret key: 256-bit random string stored in environment variable JWT_SECRET_KEY

2) Manager Comparison
   - Calculate fee efficiency: (total_fees / total_revenue) per manager
   - Revenue data source: Sum of rental_income fees from fees table where fee_type = 'rental_income'
   - Fee data source: Sum of all non-revenue fees (mgmt_fee, maintenance, misc)
   - Create comparison endpoint: GET /api/managers/comparison
   - Dashboard component with ranking table and bar chart
   - Add ranking and trend visualization over time

3) Batch Processing Optimization
   - Implement 100-record batch processing for transformations
   - Add progress tracking for large uploads
   - Error handling with partial success reporting

### Iteration 3: Real Estate Analytics & Recommendations (Priority III)
1) Property Performance Metrics
   - Calculate portfolio-level metrics:
     - ROI: (Net Operating Income / Total Investment) × 100
     - Occupancy Rate: (Occupied Units / Total Units) × 100
     - Cap Rate: (NOI / Property Value) × 100
     - Cash-on-Cash Return: (Annual Cash Flow / Cash Invested) × 100
   - Property-level metrics:
     - Rent-to-Market Ratio: (Current Rent / Market Rate) × 100
     - Maintenance Cost Ratio: (Annual Maintenance / Annual Revenue) × 100
     - Vacancy Days per year (inferred from missing rental income)
   - **Vacancy Tracking Methodology** (Option B - Inference):
     - No explicit vacancy status field in schema; inferred from fees table
     - A property is considered VACANT for a given month if:
       - No rental_income fee exists for that property in that month
       - Property exists in properties table and is not marked as 'maintenance' status
     - Calculation:
       ```
       Months_Occupied = COUNT(DISTINCT month) WHERE fees.fee_type = 'rental_income'
                         AND fees.property_id = property.id
                         AND fees.date >= (current_date - 12 months)
       Months_Vacant = 12 - Months_Occupied
       Vacancy_Days = Months_Vacant × 30
       Occupancy_Rate = (Months_Occupied / 12) × 100
       ```
     - Limitations:
       - Assumes rent is paid monthly; properties with irregular payment schedules may show false vacancies
       - Does not distinguish between tenant turnover vacancy and long-term vacancy
       - Properties under maintenance are excluded from vacancy calculations
     - Benefits:
       - No schema changes required
       - Vacancy data derived directly from actual cash flow
       - Historical vacancy trends automatically available from fees table

2) Portfolio Return Analysis
   - Calculate Expected Return:
     ```
     Expected_Return = (Annual_Revenue - Annual_Fees) / Total_Portfolio_Value
     where:
       Annual_Revenue = Sum of rental_income fees (last 12 months)
       Annual_Fees = Sum of mgmt_fee + maintenance + misc (last 12 months)
       Total_Portfolio_Value = Sum of all property current values
     ```
   - Calculate NOI (Net Operating Income):
     ```
     NOI = Total_Rental_Income - Operating_Expenses
     where:
       Operating_Expenses = mgmt_fee + maintenance + insurance + taxes (excluding mortgage)
     ```
   - Compare portfolio performance against industry benchmarks (8-12% typical real estate ROI)

3) Market Conditions Assessment
   - Calculate market status based on portfolio-wide metrics:
     ```
     Occupancy_Rate = (Occupied_Properties / Total_Properties) × 100
     Rent_Growth_Rate = ((Current_Avg_Rent - Prior_Year_Avg_Rent) / Prior_Year_Avg_Rent) × 100

     Market_Status:
       - HOT: Occupancy > 95% AND Rent_Growth > 5%
       - NORMAL: Occupancy > 85% AND Rent_Growth between -2% and 5%
       - COLD: Occupancy < 85% OR Rent_Growth < -2%
     ```
   - Occupancy calculation: Count properties with rental_income fees in the last 30 days
   - Rent growth calculation: Compare average monthly_rent over trailing 12-month periods
   - Market conditions influence recommendation thresholds (more conservative in COLD markets)

4) Hold/Sell/Acquire Recommendation Algorithm
   - **ACQUIRE** (recommend buying similar properties):
     - If ROI > 10% AND Occupancy > 90% AND Fee_Efficiency < 15%
   - **SELL** (underperforming property):
     - If ROI < 5% OR Occupancy < 70% OR Maintenance_Cost_Ratio > 30%
   - **HOLD** (maintain current portfolio): Otherwise
   - **Data Quality Metrics for Confidence Score:**
     - Data Completeness: % of required fields populated (weight: 40%)
       - High quality: >95% fields present
       - Medium quality: 80-95% fields present
       - Low quality: <80% fields present
     - Data Recency: Age of latest data (weight: 30%)
       - High quality: <30 days old
       - Medium quality: 30-90 days old
       - Low quality: >90 days old
     - Data Consistency: Variance from historical patterns (weight: 20%)
       - High quality: <10% deviation from 6-month average
       - Medium quality: 10-25% deviation
       - Low quality: >25% deviation
     - OCR Confidence: Average confidence from OCR extraction (weight: 10%)
       - High quality: >90% OCR confidence
       - Medium quality: 70-90% confidence
       - Low quality: <70% confidence
     - **Final Confidence Score Calculation:**
       ```
       Confidence = (0.4 × Completeness + 0.3 × Recency + 0.2 × Consistency + 0.1 × OCR) × 100
       ```
       - High confidence: >85%
       - Medium confidence: 60-85%
       - Low confidence: <60%

4) Async Processing (Celery + Redis)
   - Required for: OCR jobs > 10 pages, batch transformations > 500 records
   - Azure Redis Setup:
     ```bash
     az redis create \
       --name ocr-backend-redis \
       --resource-group asset-management-rg-v2 \
       --location centralus \
       --sku Basic \
       --vm-size C0
     ```
   - Celery Worker Deployment (Azure Container Instances):
     ```bash
     # Use main Dockerfile with CMD override for Celery worker
     docker build -t celery-worker:latest .

     # Deploy to ACI
     az container create \
       --resource-group asset-management-rg-v2 \
       --name celery-worker \
       --image assetmgmtsuiacr.azurecr.io/celery-worker:latest \
       --cpu 1 --memory 1 \
       --environment-variables \
         REDIS_URL=redis://ocr-backend-redis.redis.cache.windows.net:6379 \
         REDIS_PASSWORD=<access-key> \
         AZURE_SQL_SERVER=<server> \
         AZURE_SQL_DATABASE=<database> \
         AZURE_SQL_USERNAME=<username> \
         AZURE_SQL_PASSWORD=<password>
     ```
   - Flask Integration:
     ```python
     # app.py additions
     from celery import Celery
     celery = Celery('tasks', broker=os.getenv('REDIS_URL'))

     @celery.task
     def process_pdf_async(file_bytes):
         # OCR processing logic
         return extracted_data
     ```
   - Fallback: synchronous processing for smaller jobs when Redis unavailable

### Iteration 4: Production Hardening
- Database migrations via SQL scripts (no Alembic)
- Comprehensive error handling and logging
- Performance optimization with caching
- Security audit and penetration testing

## Deployment Specification
- Backend Container Image
  - Build context: `code/AssetManagementAnomalyDetection/`
  - Registry: `assetmgmtsuiacr.azurecr.io/ocr-backend-app:<tag>`
  - Multi-arch: build for `linux/amd64` using `docker buildx` on ARM64 Mac.
- Backend Web App (Linux, B1)
  - Configure container settings to ACR image and credentials.
  - App Settings: environment variables listed above + JWT_SECRET_KEY.
  - Logs: enable container logging; tail via `az webapp log tail`.
- Frontend Static Web App
  - Deploy from `frontend/build` directory
  - Custom domain: configure in Azure portal
  - Environment variables: REACT_APP_API_URL pointing to backend
  - Authentication: integrate with backend OAuth2/JWT
- Azure SQL
  - Initialize with SQL scripts (no Alembic)
  - Batch processing: optimize with bulk inserts
  - Indexes: on portfolio_id, date, fee_type for performance
- CI/CD (GitHub Actions)
  - Backend: Checkout → ACR login → buildx build/push → update Web App
  - Frontend: npm build → deploy to Static Web Apps
  - Tag scheme: `:<git-sha>`, `:latest`, `:stable` for rollback
- Rollback Strategy
  - Backend: Switch container to `:stable` tag
  - Frontend: Redeploy previous build from Git history
  - Database: Manual rollback via SQL scripts or PITR backup

## Testing Strategy
- Unit Tests (pytest)
  - OCR: parse fixtures → expected `statement_entries` with tolerances.
  - Scripts: `upload_statement_raw`, `ingest_statement_csv_to_azure`, `transform_statement_entries_to_fees`.
  - ML: `detect_anomalies` and `retrain_model` deterministic behavior under seeded data.
  - Models/API: serialization, validation, error paths.
- Integration
  - SQLite-backed end-to-end: upload → entries → fees → anomalies.
  - Azure SQL staging (or dev DB): verify connectivity, DDL, CRUD.
- E2E/Smoke (Prod)
  - `GET /`, `GET /api/portfolios`, sample detect workflow returns anomalies.
  - UI click-paths: upload → parse summary → anomalies table populated.
- Performance
  - p95 latency checks; OCR job timing; load test light concurrency.
- Security
  - File type/size validation; SQL injection checks via tests; CORS behavior; secret handling.

## Acceptance Criteria
- Uploading a supported statement yields records in `statement_raw` and `statement_entries`.
- Transform generates correct `fees` rows (date/amount/type) without duplication.
- Anomaly detection produces scores and persists to `anomalies`; API fetch paginates.
- Dashboard and anomalies UI render with live data; CSV export works.
- Deployed container at the specified App URL passes smoke tests and meets p95 targets.

## Risks & Mitigations
- OCR accuracy variance → provide mapper overrides and manual adjustments; capture lineage for audit.
- Performance on B1 → constrain job sizes; consider async/background or scale-up.
- ODBC driver/version issues → support 17/18 via env; container tests before deploy.
- Schema evolution → SQL scripts for migrations with rollback scripts and DB backups.

## Operations & Runbook
- Logs: use `az webapp log tail` for quick diagnosis; enable App Insights for telemetry.
- Common failures: DB auth (check App Settings), firewall (allow Azure services, outbound IPs), driver mismatch (switch `ODBC_DRIVER_NAME`).
- Rollback: swap to `:stable` image; verify health endpoints; consider DB PITR if migration caused issues.

## Decisions Made (Previously Open Questions)
- ✅ Authentication: OAuth2 with JWT tokens (Flask-JWT-Extended)
- ✅ Async Processing: Celery + Redis for OCR jobs > 10 pages, batch > 500 records
- ✅ Frontend Hosting: Azure Static Web Apps (separate from backend)
- ✅ Performance Metrics: Real estate-specific (ROI, occupancy, cap rate, NOI)
- ✅ Database Migrations: SQL scripts only (no Alembic)
- ✅ Manager Comparison Metric: Fee efficiency ratio (fees/revenue)
- ✅ Batch Processing Size: 100 records per batch
- ✅ Asset Type: Pure real estate property management (not securities/stocks)

## Async Processing Recommendation
Based on performance requirements and B1 tier limitations:
- **Synchronous (default)**: PDFs ≤ 10 pages, batches ≤ 100 records
- **Async Required**:
  - OCR for PDFs > 10 pages (use Celery task queue)
  - Batch transformations > 500 records
  - Portfolio performance calculations for > 10 portfolios with full history
- **Implementation**: Celery + Redis on Azure Cache for Redis (Basic tier sufficient)
- **Fallback**: Queue overflow returns HTTP 202 with job ID for polling

