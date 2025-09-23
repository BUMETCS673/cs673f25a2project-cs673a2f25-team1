# Deployment Guide

This guide explains how to deploy the Asset Management Anomaly Detection application to Render.

## Prerequisites

- GitHub repository with the code
- Render account
- PostgreSQL database (provided by Render)

## Render Deployment Steps

### 1. Create PostgreSQL Database

1. In Render dashboard, click "New +" → "PostgreSQL"
2. Choose a name (e.g., "asset-management-db")
3. Select the free tier
4. Click "Create Database"
5. Copy the **External Database URL** - you'll need this for the web service

### 2. Create Web Service

1. In Render dashboard, click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure the service:

**Basic Settings:**
- **Name**: `asset-management-api` (or your preferred name)
- **Root Directory**: `AssetManagementAnomalyDetection`
- **Environment**: `Python 3`
- **Branch**: `main` (or your default branch)

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt && python init_db.py`
- **Start Command**: `gunicorn app:app`

**Environment Variables:**
- `DATABASE_URL`: Paste the PostgreSQL URL from step 1
- `FLASK_ENV`: `production`
- `SECRET_KEY`: Generate a secure random string
- `CORS_ORIGINS`: `*` (or specific domains for production)

### 3. Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Install dependencies
   - Initialize the database with sample data
   - Start the Flask application with Gunicorn

### 4. Test the API

Once deployed, you can test the API endpoints:

- `GET https://your-app-name.onrender.com/` - Health check
- `GET https://your-app-name.onrender.com/api/portfolios` - List portfolios
- `GET https://your-app-name.onrender.com/api/anomalies/{portfolio_id}` - Get anomalies
- `POST https://your-app-name.onrender.com/api/detect-anomalies/{portfolio_id}` - Run anomaly detection

## Local Development

### Setup

1. Clone the repository
2. Navigate to the AssetManagementAnomalyDetection directory
3. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Initialize the database:
   ```bash
   python sample_data.py
   ```
6. Run the application:
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

### Environment Variables (Local)

Create a `.env` file in the AssetManagementAnomalyDetection directory:

```env
FLASK_ENV=development
DATABASE_URL=sqlite:///instance/asset_management.db
SECRET_KEY=dev-secret-key
CORS_ORIGINS=*
```

## Database Configuration

The application automatically detects the database type based on the `DATABASE_URL`:

- **SQLite** (development): `sqlite:///instance/asset_management.db`
- **PostgreSQL** (production): `postgresql://user:pass@host:port/db`

## Frontend Deployment

To deploy the React frontend:

1. **Vercel** (recommended):
   - Connect your GitHub repository
   - Set root directory to `AssetManagementAnomalyDetection/frontend`
   - Add environment variable: `REACT_APP_API_URL=https://your-backend.onrender.com`

2. **Netlify**:
   - Connect your GitHub repository
   - Set base directory to `AssetManagementAnomalyDetection/frontend`
   - Build command: `npm run build`
   - Publish directory: `build`

## Troubleshooting

### Common Issues

1. **Database connection errors**: Ensure `DATABASE_URL` is correctly set
2. **Build failures**: Check that all dependencies are in `requirements.txt`
3. **CORS errors**: Verify `CORS_ORIGINS` includes your frontend domain
4. **Port binding**: Render automatically sets the `PORT` environment variable

### Logs

Check Render logs for debugging:
- Go to your service dashboard
- Click "Logs" tab
- Look for error messages during build or runtime

## Security Notes

- Change the default `SECRET_KEY` in production
- Use specific `CORS_ORIGINS` instead of `*` in production
- Consider using environment-specific configurations
- Regularly update dependencies for security patches
