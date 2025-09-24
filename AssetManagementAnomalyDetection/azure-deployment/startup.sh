#!/bin/bash

# Azure App Service startup script for Python Flask app

# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=production

# Start the Flask application with Gunicorn
gunicorn --bind=0.0.0.0 --timeout 600 app:app
