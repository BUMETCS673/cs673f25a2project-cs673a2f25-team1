# PR: OCR Backend Implementation with Azure Deployment

## 🎯 Overview
This PR implements a complete OCR (Optical Character Recognition) backend service that processes PDF rental statements and extracts financial data. The service is containerized with Docker and deployed to Azure, providing a publicly accessible API endpoint for PDF processing.

## 🚀 What's Been Built

### 1. **OCR Processing Backend**
- **New OCR Module** (`code/AssetManagementAnomalyDetection/ocr/processor.py`)
  - Processes PDF files and extracts financial data (rent, management fees, repairs, deposits, etc.)
  - Uses dual-method approach: `pdftotext` for text PDFs, fallback to Tesseract OCR for scanned images
  - Provides confidence scores for each extracted field
  - Achieves 84% accuracy on test documents

- **Flask API Endpoint** (`/api/upload-pdf`)
  - Accepts multipart/form-data PDF uploads
  - Returns JSON with extracted data and confidence scores
  - Proper error handling for missing or invalid files

### 2. **Docker Containerization**
- **Multi-platform Docker Support**
  - AMD64 image for Azure deployment (353MB)
  - ARM64 image for local Mac development (1.37GB)
  - Includes all OCR dependencies (Poppler, Tesseract)
  - Production-ready with Gunicorn WSGI server

### 3. **Azure Cloud Deployment**
- **Live Production Endpoint**: https://ocr-backend-app.azurewebsites.net/
  - Publicly accessible without authentication
  - Azure Container Registry: `assetmgmtsuiacr`
  - Azure App Service: `ocr-backend-app` (B1 tier)
  - Handles cold starts gracefully (30-60 seconds on first request)

### 4. **Frontend Integration**
- **React Component** (`frontend/src/components/PDFUploadTest.tsx`)
  - Material-UI styled upload interface
  - Drag & drop file upload
  - Toggle between Azure and local endpoints
  - Visual display of extracted data with confidence scores

- **Standalone Test Page** (`pdf-upload-test.html`)
  - Works independently without React
  - Publicly accessible via GitHub
  - Mobile-responsive design

### 5. **Documentation**
- `AZURE_DEPLOYMENT.md` - Complete Azure deployment guide
- `DOCKER_TEST_RESULTS.md` - Docker implementation test results
- `FULL_TEST_RESULTS.md` - Comprehensive test suite results
- `run_tests.sh` - Automated test script

## 📋 Files Changed

### New Files:
- `code/AssetManagementAnomalyDetection/ocr/processor.py` - OCR processing module
- `code/AssetManagementAnomalyDetection/ocr/__init__.py` - Module initialization
- `code/AssetManagementAnomalyDetection/Dockerfile` - Docker configuration
- `code/AssetManagementAnomalyDetection/.dockerignore` - Docker ignore rules
- `code/AssetManagementAnomalyDetection/AZURE_DEPLOYMENT.md` - Deployment guide
- `code/AssetManagementAnomalyDetection/DOCKER_TEST_RESULTS.md` - Test results
- `code/AssetManagementAnomalyDetection/test-upload.html` - Browser test page
- `code/AssetManagementAnomalyDetection/run_tests.sh` - Test script
- `frontend/src/components/PDFUploadTest.tsx` - React component
- `pdf-upload-test.html` - Standalone public test page

### Modified Files:
- `code/AssetManagementAnomalyDetection/app.py` - Added `/api/upload-pdf` endpoint
- `code/AssetManagementAnomalyDetection/requirements.txt` - Added OCR dependencies
- `frontend/src/App.tsx` - Added link to PDF test page
- `frontend/package.json` - Added gh-pages deployment configuration

## 🧪 How to Test

### 1. **Test Public Azure Endpoint (No Setup Required)**

#### Via Browser:
Open this link in any browser:
```
https://htmlpreview.github.io/?https://github.com/BUMETCS673/cs673f25a2project-cs673a2f25-team1/blob/feat/OCR-backend/pdf-upload-test.html
```

#### Via cURL:
```bash
# Test health check
curl https://ocr-backend-app.azurewebsites.net/

# Test PDF upload (use any PDF file)
curl -X POST https://ocr-backend-app.azurewebsites.net/api/upload-pdf \
  -F "file=@your-pdf-file.pdf"
```

### 2. **Test Locally**

#### Start the Flask backend:
```bash
cd code/AssetManagementAnomalyDetection
python app.py
# Server runs on http://127.0.0.1:5001
```

#### Test with sample PDFs:
```bash
# Health check
curl http://127.0.0.1:5001/

# Upload sample PDF
curl -X POST http://127.0.0.1:5001/api/upload-pdf \
  -F "file=@../sample-data/rental-statements/property-a/20230725.pdf"
```

### 3. **Test with Docker**

```bash
cd code/AssetManagementAnomalyDetection

# Build Docker image
docker build -t ocr-backend:latest .

# Run container
docker run -d -p 8000:8000 --name ocr-test ocr-backend:latest

# Test endpoint
curl http://localhost:8000/api/upload-pdf \
  -F "file=@../sample-data/rental-statements/property-a/20230725.pdf"
```

### 4. **Run Automated Tests**

```bash
cd code/AssetManagementAnomalyDetection
./run_tests.sh
```

Expected output:
```
✅ Local Server Tests - PASSING
✅ Docker Tests - PASSING
✅ Azure Tests - PASSING
✅ PDF Processing - PASSING (84% accuracy)
```

## 📊 Expected Results

When uploading `sample-data/rental-statements/property-a/20230725.pdf`:

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
  "field_confidences": {
    "rent": 0.95,
    "management_fee": 0.95,
    "total": 0.95
  }
}
```

## ✅ Acceptance Criteria Met

- [x] OCR backend processes PDFs and extracts financial data
- [x] REST API endpoint accepts file uploads
- [x] Docker container builds and runs successfully
- [x] Deployed to Azure with public accessibility
- [x] Frontend integration with upload interface
- [x] Confidence scoring for extracted data
- [x] Error handling for invalid inputs
- [x] Comprehensive documentation
- [x] Automated test suite

## 🔗 Live Demo

**Public Test Page**: https://htmlpreview.github.io/?https://github.com/BUMETCS673/cs673f25a2project-cs673a2f25-team1/blob/feat/OCR-backend/pdf-upload-test.html

**Azure API Endpoint**: https://ocr-backend-app.azurewebsites.net/

## 📝 Notes

- First request to Azure may take 30-60 seconds due to cold start on B1 tier
- OCR accuracy is 84% on test documents
- Supports both text-based and scanned PDFs
- No authentication required for testing purposes
- Monthly Azure cost: ~$60 (B1 App Service + ACR)

## 🚨 Known Issues

- Cold start delays on Azure B1 tier (expected behavior)
- Large PDFs may timeout on first request (retry usually succeeds)

## 📚 Related Documentation

- [Azure Deployment Guide](code/AssetManagementAnomalyDetection/AZURE_DEPLOYMENT.md)
- [Docker Test Results](code/AssetManagementAnomalyDetection/DOCKER_TEST_RESULTS.md)
- [Full Test Results](code/AssetManagementAnomalyDetection/FULL_TEST_RESULTS.md)