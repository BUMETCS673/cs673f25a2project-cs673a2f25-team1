#!/bin/bash

# Quick Azure Setup Script
# This script prepares your project for Azure deployment

echo "🚀 Preparing Asset Management Anomaly Detection for Azure deployment..."

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first:"
    echo "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo "🔐 Please log in to Azure first:"
    echo "   az login"
    exit 1
fi

# Copy deployment files to root directory
echo "📁 Copying Azure deployment files..."
cp azure-deployment/web.config .
cp azure-deployment/startup.sh .
cp azure-deployment/.deployment .

# Update requirements.txt to include pyodbc
echo "📦 Updating requirements.txt..."
if ! grep -q "pyodbc" requirements.txt; then
    echo "pyodbc>=4.0.34" >> requirements.txt
    echo "✅ Added pyodbc to requirements.txt"
fi

# Create .env template if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env template..."
    cp azure-deployment/.env.template .env
    echo "✅ Created .env file. Please update it with your Azure SQL Database details."
fi

echo ""
echo "✅ Project prepared for Azure deployment!"
echo ""
echo "📋 Next steps:"
echo "1. Update .env file with your Azure SQL Database details"
echo "2. Run: ./azure-deployment/deploy.sh (Linux/Mac) or azure-deployment/deploy.bat (Windows)"
echo "3. Follow the deployment guide: azure-deployment/AZURE_DEPLOYMENT_GUIDE.md"
echo ""
echo "🔗 Your app will be available at: https://asset-management-api.azurewebsites.net"
