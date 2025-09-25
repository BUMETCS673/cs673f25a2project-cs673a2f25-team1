#!/bin/bash

# Azure CLI deployment script for Asset Management Anomaly Detection System
# Prerequisites: Azure CLI installed and logged in

set -e

# Configuration variables - UPDATE THESE
RESOURCE_GROUP="asset-management-rg"
LOCATION="westus2"
APP_NAME="asset-management-api"
SQL_SERVER_NAME="asset-management-sql"
SQL_DATABASE_NAME="AssetManagementDB"
SQL_ADMIN_USER="sqladmin"
SQL_ADMIN_PASSWORD="YourSecurePassword123!"

echo "🚀 Starting Azure deployment..."

# Create resource group
echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create SQL Server
echo "🗄️ Creating Azure SQL Server..."
az sql server create \
    --resource-group $RESOURCE_GROUP \
    --name $SQL_SERVER_NAME \
    --location $LOCATION \
    --admin-user $SQL_ADMIN_USER \
    --admin-password $SQL_ADMIN_PASSWORD

# Create SQL Database
echo "📊 Creating Azure SQL Database..."
az sql db create \
    --resource-group $RESOURCE_GROUP \
    --server $SQL_SERVER_NAME \
    --name $SQL_DATABASE_NAME \
    --service-objective Basic

# Configure firewall rule to allow Azure services
echo "🔥 Configuring firewall rules..."
az sql server firewall-rule create \
    --resource-group $RESOURCE_GROUP \
    --server $SQL_SERVER_NAME \
    --name "AllowAzureServices" \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0

# Create App Service plan
echo "📋 Creating App Service plan..."
az appservice plan create \
    --name "${APP_NAME}-plan" \
    --resource-group $RESOURCE_GROUP \
    --sku F1 \
    --is-linux

# Create App Service
echo "🌐 Creating App Service..."
az webapp create \
    --resource-group $RESOURCE_GROUP \
    --plan "${APP_NAME}-plan" \
    --name $APP_NAME \
    --runtime "PYTHON|3.9"

# Configure app settings
echo "⚙️ Configuring app settings..."
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
        AZURE_SQL_SERVER=$SQL_SERVER_NAME \
        AZURE_SQL_DATABASE=$SQL_DATABASE_NAME \
        AZURE_SQL_USERNAME=$SQL_ADMIN_USER \
        AZURE_SQL_PASSWORD=$SQL_ADMIN_PASSWORD \
        FLASK_ENV=production \
        FLASK_APP=app.py

echo "✅ Azure resources created successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Deploy your code using: az webapp deployment source config-zip --resource-group $RESOURCE_GROUP --name $APP_NAME --src deployment.zip"
echo "2. Initialize database by running azure-db-init.sql in Azure SQL Database"
echo "3. Your API will be available at: https://$APP_NAME.azurewebsites.net"
echo ""
echo "🔗 Useful commands:"
echo "- View logs: az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME"
echo "- Restart app: az webapp restart --resource-group $RESOURCE_GROUP --name $APP_NAME"
echo "- Delete resources: az group delete --name $RESOURCE_GROUP --yes"
