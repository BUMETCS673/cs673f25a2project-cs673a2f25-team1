# Azure Deployment Guide for OCR Backend

This guide walks through deploying the PDF OCR backend to Azure using Docker containers.

## Prerequisites

- Azure CLI installed (`az --version`)
- Docker Desktop installed and running
- Azure subscription with appropriate permissions
- Git repository with current code

## Option 1: Deploy to Azure Container Instances (Quickest)

### Step 1: Login to Azure
```bash
az login
```

### Step 2: Create Resource Group (if needed)
```bash
# Replace 'your-rg' with your resource group name
# Replace 'eastus' with your preferred region
az group create --name your-rg --location eastus
```

### Step 3: Create Azure Container Registry (ACR)
```bash
# Replace 'youracr' with a unique registry name (lowercase, no spaces)
az acr create \
  --resource-group your-rg \
  --name youracr \
  --sku Basic \
  --admin-enabled true
```

### Step 4: Build and Push Image to ACR
```bash
# Build and push in one command
az acr build \
  --registry youracr \
  --image ocr-backend:latest \
  .
```

### Step 5: Deploy to Container Instances
```bash
# Get ACR credentials
ACR_PASSWORD=$(az acr credential show --name youracr --query "passwords[0].value" -o tsv)

# Deploy container
az container create \
  --resource-group your-rg \
  --name ocr-backend \
  --image youracr.azurecr.io/ocr-backend:latest \
  --registry-username youracr \
  --registry-password $ACR_PASSWORD \
  --dns-name-label your-unique-name \
  --ports 8000 \
  --cpu 1 \
  --memory 2 \
  --environment-variables \
    FLASK_ENV=production \
    USE_LOCAL_SQLITE=true
```

### Step 6: Get Public URL
```bash
az container show \
  --resource-group your-rg \
  --name ocr-backend \
  --query "ipAddress.fqdn" \
  --output tsv
```

Your API will be available at: `http://your-unique-name.eastus.azurecontainer.io:8000`

### Step 7: Test the Endpoint
```bash
# Replace URL with your actual container URL
curl -X POST http://your-unique-name.eastus.azurecontainer.io:8000/api/upload-pdf \
  -F "file=@sample.pdf"
```

## Option 2: Deploy to Azure App Service (Production-Ready)

### Steps 1-4: Same as Option 1 (Login, Create RG, Create ACR, Build Image)

### Step 5: Create App Service Plan
```bash
az appservice plan create \
  --name your-app-plan \
  --resource-group your-rg \
  --is-linux \
  --sku B1
```

### Step 6: Create Web App with Container
```bash
az webapp create \
  --resource-group your-rg \
  --plan your-app-plan \
  --name your-app-name \
  --deployment-container-image-name youracr.azurecr.io/ocr-backend:latest
```

### Step 7: Configure Registry Credentials
```bash
# Get ACR credentials
ACR_PASSWORD=$(az acr credential show --name youracr --query "passwords[0].value" -o tsv)

# Configure web app to use ACR
az webapp config container set \
  --name your-app-name \
  --resource-group your-rg \
  --docker-custom-image-name youracr.azurecr.io/ocr-backend:latest \
  --docker-registry-server-url https://youracr.azurecr.io \
  --docker-registry-server-user youracr \
  --docker-registry-server-password $ACR_PASSWORD
```

### Step 8: Configure Environment Variables
```bash
az webapp config appsettings set \
  --resource-group your-rg \
  --name your-app-name \
  --settings \
    FLASK_ENV=production \
    USE_LOCAL_SQLITE=true \
    PORT=8000 \
    WEBSITES_PORT=8000
```

### Step 9: Get Public URL
```bash
echo "https://your-app-name.azurewebsites.net"
```

### Step 10: Test the Endpoint
```bash
curl -X POST https://your-app-name.azurewebsites.net/api/upload-pdf \
  -F "file=@sample.pdf"
```

## Using Azure SQL Database (Optional)

If you want to use Azure SQL instead of SQLite:

### Create Azure SQL Database
```bash
# Create SQL server
az sql server create \
  --name your-sql-server \
  --resource-group your-rg \
  --location eastus \
  --admin-user sqladmin \
  --admin-password YourStrongPassword123!

# Create database
az sql db create \
  --resource-group your-rg \
  --server your-sql-server \
  --name your-database \
  --service-objective S0

# Allow Azure services
az sql server firewall-rule create \
  --resource-group your-rg \
  --server your-sql-server \
  --name AllowAzure \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

### Update Container Environment Variables
```bash
# For Container Instances
az container create \
  ... \
  --environment-variables \
    FLASK_ENV=production \
    AZURE_SQL_SERVER=your-sql-server \
    AZURE_SQL_DATABASE=your-database \
    AZURE_SQL_USERNAME=sqladmin \
    AZURE_SQL_PASSWORD=YourStrongPassword123!

# For App Service
az webapp config appsettings set \
  ... \
  --settings \
    AZURE_SQL_SERVER=your-sql-server \
    AZURE_SQL_DATABASE=your-database \
    AZURE_SQL_USERNAME=sqladmin \
    AZURE_SQL_PASSWORD=YourStrongPassword123!
```

## Monitoring and Logs

### View Container Logs (Container Instances)
```bash
az container logs \
  --resource-group your-rg \
  --name ocr-backend
```

### View App Service Logs
```bash
az webapp log tail \
  --resource-group your-rg \
  --name your-app-name
```

## Cleanup Resources

To avoid charges, delete resources when done testing:

```bash
# Delete entire resource group (removes everything)
az group delete --name your-rg --yes

# Or delete individual resources
az container delete --resource-group your-rg --name ocr-backend --yes
az webapp delete --resource-group your-rg --name your-app-name
az acr delete --resource-group your-rg --name youracr --yes
```

## Troubleshooting

### Container won't start
- Check logs: `az container logs --resource-group your-rg --name ocr-backend`
- Verify image exists in ACR: `az acr repository list --name youracr`

### OCR not working
- Ensure Poppler and Tesseract are installed (they are in the Dockerfile)
- Check container has enough memory (minimum 2GB recommended)

### Database connection issues
- Verify Azure SQL firewall rules allow Azure services
- Check environment variables are set correctly
- Test connection string locally first

## Cost Estimates (as of 2024)

- **Container Instances**: ~$35/month (1 vCPU, 2GB RAM)
- **App Service B1**: ~$55/month
- **Azure SQL Basic**: ~$5/month
- **Container Registry Basic**: ~$5/month

## Summary

Your OCR backend is now deployed to Azure and accessible via:

- **Container Instances**: `http://your-unique-name.region.azurecontainer.io:8000/api/upload-pdf`
- **App Service**: `https://your-app-name.azurewebsites.net/api/upload-pdf`

Test with:
```bash
curl -X POST [YOUR_URL]/api/upload-pdf -F "file=@statement.pdf"
```