# Azure Deployment Files

This directory contains all the necessary files and scripts to deploy the Asset Management Anomaly Detection System to Azure.

## 📁 Files Overview

### Configuration Files
- **`web.config`** - IIS configuration for Windows App Service
- **`startup.sh`** - Linux startup script for App Service
- **`.deployment`** - Deployment configuration
- **`azure-db-init.sql`** - Database initialization script

### Environment Configuration
- **`.env.template`** - Template for local environment variables
- **`azure-env-vars.txt`** - Azure App Service environment variables

### Deployment Scripts
- **`deploy.sh`** - Automated deployment script (Linux/Mac)
- **`deploy.bat`** - Automated deployment script (Windows)
- **`setup.sh`** - Quick setup script to prepare project

### Documentation
- **`AZURE_DEPLOYMENT_GUIDE.md`** - Complete step-by-step deployment guide

## 🚀 Quick Start

1. **Prepare your project:**
   ```bash
   chmod +x azure-deployment/setup.sh
   ./azure-deployment/setup.sh
   ```

2. **Deploy to Azure:**
   ```bash
   # Linux/Mac
   ./azure-deployment/deploy.sh
   
   # Windows
   azure-deployment/deploy.bat
   ```

3. **Follow the detailed guide:**
   - Read `AZURE_DEPLOYMENT_GUIDE.md` for complete instructions

## 📋 Prerequisites

- Azure CLI installed and configured
- Azure subscription
- Git (for code deployment)

## 💰 Estimated Costs

- **Basic Setup**: ~$15-30/month
- **Free Tier**: Available with usage limits

## 🔧 Customization

Before running deployment scripts, update these variables in `deploy.sh` or `deploy.bat`:

```bash
RESOURCE_GROUP="asset-management-rg"
LOCATION="eastus"
APP_NAME="asset-management-api"
SQL_SERVER_NAME="asset-management-sql"
SQL_DATABASE_NAME="AssetManagementDB"
SQL_ADMIN_USER="sqladmin"
SQL_ADMIN_PASSWORD="YourSecurePassword123!"
```

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section in `AZURE_DEPLOYMENT_GUIDE.md`
2. Review Azure App Service logs
3. Verify database connectivity
4. Check environment variables

## 📞 Useful Commands

```bash
# View application logs
az webapp log tail --resource-group asset-management-rg --name asset-management-api

# Restart the application
az webapp restart --resource-group asset-management-rg --name asset-management-api

# Delete all resources (cleanup)
az group delete --name asset-management-rg --yes
```

Happy deploying! 🎉
