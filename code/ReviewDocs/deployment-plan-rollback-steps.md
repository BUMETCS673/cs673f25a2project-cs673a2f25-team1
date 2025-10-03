Intended deployment plan (student-friendly)
Environment
- Backend: Azure App Service (Linux, Basic/Free), Python 3.9
- Database: Azure SQL (Basic), or local SQLite for dev
- Frontend: Azure Static Web Apps or App Service (served from CRA build)
- Config: App Settings for secrets (no .env in repo)
- Deploy steps
Backend
- Build/package: zip source
- Deploy: az webapp deploy --type zip --src deployment.zip
- App settings: AZURE_SQL_SERVER, AZURE_SQL_DATABASE, AZURE_SQL_USERNAME, - AZURE_SQL_PASSWORD, FLASK_ENV=production
Frontend
- npm ci && npm run build
- Upload build/ to Static Web Apps or serve via App Service
- Post-deploy checks
- Health: GET /
- API: GET /api/portfolios
- Frontend: open site URL and click through dashboard
Rollback steps
- Maintain local data is SQL server format (assume this step is satisfied.)
If failure:
- Backend: az webapp deploy --type zip --src deployment-prev.zip
- Frontend: restore previous build (or SWA previous deployment)
If config issue:
- Revert changed App Settings to last known-good values
- Verify same post-deploy checks