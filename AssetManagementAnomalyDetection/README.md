# Asset Management Anomaly Detection System

A machine learning-powered system to detect anomalously high management fees in asset portfolios, helping portfolio owners identify cost-reduction opportunities despite imperfect data.

## Architecture

- **Backend**: Python Flask API with SQLAlchemy ORM
- **Database**: Microsoft SQL Server
- **Frontend**: React TypeScript application with Material-UI
- **ML**: Scikit-learn Isolation Forest for anomaly detection

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 16+
- Microsoft SQL Server
- ODBC Driver 17 for SQL Server

### Backend Setup

1. **Create virtual environment**:
   ```bash
   cd AssetManagementAnomalyDetection
   python -m venv venv
   ```

2. **Activate virtual environment**:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Database setup**:
   - Run `db_init.sql` in Microsoft SQL Server Management Studio
   - Update `.env` with your database connection string

5. **Run the Flask app**:
   ```bash
   python app.py
   ```

### Frontend Setup

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**:
   ```bash
   npm start
   ```

The frontend will proxy API requests to `http://localhost:5000`.

## API Endpoints

- `GET /api/portfolios` - List all portfolios
- `GET /api/anomalies/<portfolio_id>` - Get anomalies for a portfolio
- `POST /api/detect-anomalies/<portfolio_id>` - Run anomaly detection

## ML Model

The system uses Isolation Forest algorithm to detect anomalies in management fee data. The model:

- Handles missing and noisy data
- Uses rolling statistics for trend analysis
- Automatically retrains with new data
- Provides anomaly scores for prioritization

## Database Schema

- `portfolios`: Portfolio information
- `assets`: Individual assets in portfolios
- `fees`: Management fees with timestamps
- `anomalies`: Detected anomalies with scores

## Deployment

For production deployment:

1. Set `FLASK_ENV=production` in `.env`
2. Use Gunicorn for serving Flask app
3. Configure database connection for production
4. Build React app with `npm run build`
5. Serve static files through Flask or web server

## Features

- Real-time anomaly detection
- Interactive dashboard with charts
- Portfolio management interface
- Regulatory-compliant data handling
- Scalable architecture for large datasets
