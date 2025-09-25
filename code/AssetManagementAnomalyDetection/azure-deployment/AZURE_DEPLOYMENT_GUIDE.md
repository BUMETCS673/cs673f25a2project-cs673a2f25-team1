# 🚀 Complete Azure Deployment Guide
## Asset Management Anomaly Detection System

This guide will walk you through deploying your Flask backend to Azure App Service with Azure SQL Database.

## 📋 Prerequisites

### Required Software
- **Azure CLI** - [Download here](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- **Git** - [Download here](https://git-scm.com/downloads)
- **Python 3.9+** (for local testing)

### Azure Account
- **Azure Subscription** - [Free account available](https://azure.microsoft.com/en-us/free/)
- **Estimated Cost**: ~$15-30/month for basic setup

## 🎯 Step-by-Step Deployment

### Step 1: Install and Configure Azure CLI

#### Windows:
```bash
# Download and install Azure CLI from Microsoft website
# Then restart your terminal/command prompt
```

#### macOS:
```bash
brew install azure-cli
```

#### Linux:
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

#### Login to Azure:
```bash
az login
# Follow the browser authentication process
```

### Step 2: Prepare Your Code

1. **Navigate to your project directory:**
   ```bash
   cd AssetManagementAnomalyDetection
   ```

2. **Copy deployment files to root directory:**
   ```bash
   cp azure-deployment/* .
   ```

3. **Update requirements.txt** (add missing dependencies):
   ```bash
   echo "pyodbc>=4.0.34" >> requirements.txt
   ```

### Step 3: Deploy Azure Resources

#### Option A: Automated Deployment (Recommended)

**For Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**For Windows:**
```cmd
deploy.bat
```

#### Option B: Manual Deployment

1. **Create Resource Group:**
   ```bash
   az group create --name asset-management-rg --location eastus
   ```

2. **Create SQL Server:**
   ```bash
   az sql server create \
     --resource-group asset-management-rg \
     --name asset-management-sql \
     --location eastus \
     --admin-user sqladmin \
     --admin-password YourSecurePassword123!
   ```

3. **Create SQL Database:**
   ```bash
   az sql db create \
     --resource-group asset-management-rg \
     --server asset-management-sql \
     --name AssetManagementDB \
     --service-objective Basic
   ```

4. **Configure Firewall:**
   ```bash
   az sql server firewall-rule create \
     --resource-group asset-management-rg \
     --server asset-management-sql \
     --name "AllowAzureServices" \
     --start-ip-address 0.0.0.0 \
     --end-ip-address 0.0.0.0
   ```

5. **Create App Service Plan:**
   ```bash
   az appservice plan create \
     --name asset-management-api-plan \
     --resource-group asset-management-rg \
     --sku B1 \
     --is-linux
   ```

6. **Create App Service:**
   ```bash
   az webapp create \
     --resource-group asset-management-rg \
     --plan asset-management-api-plan \
     --name asset-management-api \
     --runtime "PYTHON|3.9"
   ```

7. **Configure Environment Variables:**
   ```bash
   az webapp config appsettings set \
     --resource-group asset-management-rg \
     --name asset-management-api \
     --settings \
       AZURE_SQL_SERVER=asset-management-sql \
       AZURE_SQL_DATABASE=AssetManagementDB \
       AZURE_SQL_USERNAME=sqladmin \
       AZURE_SQL_PASSWORD=YourSecurePassword123! \
       FLASK_ENV=production \
       FLASK_APP=app.py
   ```

### Step 4: Deploy Your Code

1. **Create deployment package:**
   ```bash
   # Create a zip file with your application
   zip -r deployment.zip . -x "*.git*" "*node_modules*" "*__pycache__*" "*.pyc" "*.env*"
   ```

2. **Deploy to Azure:**
   ```bash
   az webapp deployment source config-zip \
     --resource-group asset-management-rg \
     --name asset-management-api \
     --src deployment.zip
   ```

### Step 5: Initialize Database

1. **Connect to Azure SQL Database:**
   - Go to [Azure Portal](https://portal.azure.com)
   - Navigate to your SQL Database
   - Click "Query editor" or use SQL Server Management Studio

2. **Run the initialization script:**
   ```sql
   -- Copy and paste the contents of azure-db-init.sql
   -- This will create tables and insert sample data
   ```

### Step 6: Test Your Deployment

1. **Get your app URL:**
   ```bash
   az webapp show --resource-group asset-management-rg --name asset-management-api --query defaultHostName --output tsv
   ```

2. **Test the API:**
   ```bash
   curl https://your-app-name.azurewebsites.net/
   # Should return: {"message": "Asset Management Anomaly Detection API"}
   ```

3. **Test database connection:**
   ```bash
   curl https://your-app-name.azurewebsites.net/api/portfolios
   # Should return portfolio data
   ```

## 🔧 Configuration Details

### Environment Variables
Your app uses these environment variables in Azure:

| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_SQL_SERVER` | SQL Server name | `asset-management-sql` |
| `AZURE_SQL_DATABASE` | Database name | `AssetManagementDB` |
| `AZURE_SQL_USERNAME` | SQL admin username | `sqladmin` |
| `AZURE_SQL_PASSWORD` | SQL admin password | `YourSecurePassword123!` |
| `FLASK_ENV` | Flask environment | `production` |
| `FLASK_APP` | Flask app file | `app.py` |

### Database Connection
The app automatically detects Azure environment and uses the appropriate connection string:
- **Azure**: Uses Azure SQL Database with proper encryption
- **Local**: Falls back to local SQL Server

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Errors:**
   ```bash
   # Check firewall rules
   az sql server firewall-rule list --resource-group asset-management-rg --server asset-management-sql
   
   # Check app settings
   az webapp config appsettings list --resource-group asset-management-rg --name asset-management-api
   ```

2. **Deployment Failures:**
   ```bash
   # View deployment logs
   az webapp log tail --resource-group asset-management-rg --name asset-management-api
   ```

3. **Python Package Issues:**
   ```bash
   # Check if all dependencies are in requirements.txt
   # Ensure pyodbc is included for SQL Server connectivity
   ```

### Useful Commands

```bash
# View application logs
az webapp log tail --resource-group asset-management-rg --name asset-management-api

# Restart the application
az webapp restart --resource-group asset-management-rg --name asset-management-api

# Update app settings
az webapp config appsettings set --resource-group asset-management-rg --name asset-management-api --settings NEW_SETTING=value

# Delete all resources (cleanup)
az group delete --name asset-management-rg --yes
```

## 💰 Cost Optimization

### Basic Setup (~$15-30/month):
- **App Service Plan B1**: ~$13/month
- **Azure SQL Database Basic**: ~$5/month
- **Storage**: ~$1/month

### Free Tier Options:
- **App Service F1**: Free (with limitations)
- **Azure SQL Database DTU**: Free tier available
- **Total**: $0/month (with usage limits)

## 🔒 Security Best Practices

1. **Use Azure Key Vault** for sensitive data:
   ```bash
   # Create Key Vault
   az keyvault create --name your-keyvault --resource-group asset-management-rg
   
   # Store password
   az keyvault secret set --vault-name your-keyvault --name sql-password --value YourSecurePassword123!
   ```

2. **Enable HTTPS** (automatic with Azure App Service)

3. **Configure CORS** properly for production

4. **Use Managed Identity** for database connections (advanced)

## 📊 Monitoring and Scaling

### Application Insights
```bash
# Enable Application Insights
az monitor app-insights component create \
  --resource-group asset-management-rg \
  --app asset-management-api \
  --location eastus \
  --kind web
```

### Scaling
```bash
# Scale up App Service Plan
az appservice plan update --resource-group asset-management-rg --name asset-management-api-plan --sku S1

# Scale out (multiple instances)
az webapp config set --resource-group asset-management-rg --name asset-management-api --number-of-workers 2
```

## 🎉 Success!

Your Flask backend is now running on Azure! 

**Your API endpoints:**
- `https://your-app-name.azurewebsites.net/` - Health check
- `https://your-app-name.azurewebsites.net/api/portfolios` - List portfolios
- `https://your-app-name.azurewebsites.net/api/anomalies/<id>` - Get anomalies
- `https://your-app-name.azurewebsites.net/api/detect-anomalies/<id>` - Run detection

**Next Steps:**
1. Deploy your React frontend to Azure Static Web Apps
2. Set up CI/CD with GitHub Actions
3. Configure custom domain
4. Add monitoring and alerting

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Azure App Service logs
3. Verify database connectivity
4. Check environment variables

Happy deploying! 🚀
