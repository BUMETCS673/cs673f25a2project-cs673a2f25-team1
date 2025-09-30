FROM python:3.9-slim

# Install system dependencies including OCR tools
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    unixodbc-dev \
    curl \
    gnupg \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Install Microsoft ODBC Driver (optional - only needed if using Azure SQL)
# Using updated method for adding repository keys (apt-key is deprecated)
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft.gpg \
    && echo "deb [arch=amd64,arm64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 || echo "ODBC driver installation failed - will use SQLite fallback"

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Azure App Service expects 8000 by default)
EXPOSE 8000

# Set environment variables for production
ENV FLASK_ENV=production
ENV PORT=8000

# Run the application with Gunicorn (production WSGI server)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "120", "--workers", "2", "app:app"]
