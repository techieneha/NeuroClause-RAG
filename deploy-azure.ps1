# PowerShell script for Windows users
# Azure Container Apps Deployment Script

# Variables - Update these
$RESOURCE_GROUP = "neuroclause-rg"
$LOCATION = "eastus2"
$CONTAINER_APP_ENV = "neuroclause-env"
$CONTAINER_APP_NAME = "neuroclause-app"
$CONTAINER_REGISTRY = "neuroclaregistry"
$IMAGE_NAME = "neuroclause-rag"
$TEAM_TOKEN = "your_hackrx_token_here"  # Replace with your actual token

Write-Host "🚀 Starting Azure Container Apps Deployment..." -ForegroundColor Green

# 1. Login to Azure
Write-Host "📝 Logging in to Azure..." -ForegroundColor Yellow
az login

# 2. Install Container Apps extension if not already installed
Write-Host "🔧 Installing Container Apps extension..." -ForegroundColor Yellow
az extension add --name containerapp --upgrade

# 3. Create Resource Group
Write-Host "📦 Creating resource group..." -ForegroundColor Yellow
az group create --name $RESOURCE_GROUP --location $LOCATION

# 4. Create Container Registry (Free tier)
Write-Host "🏗️ Creating Container Registry..." -ForegroundColor Yellow
az acr create --resource-group $RESOURCE_GROUP --name $CONTAINER_REGISTRY --sku Basic --admin-enabled true

# 5. Build and push Docker image
Write-Host "🐳 Building and pushing Docker image..." -ForegroundColor Yellow
az acr build --registry $CONTAINER_REGISTRY --image "${IMAGE_NAME}:latest" .

# 6. Create Container Apps Environment
Write-Host "🌍 Creating Container Apps Environment..." -ForegroundColor Yellow
az containerapp env create `
  --name $CONTAINER_APP_ENV `
  --resource-group $RESOURCE_GROUP `
  --location $LOCATION

# 7. Deploy Container App
Write-Host "🚀 Deploying Container App..." -ForegroundColor Yellow
az containerapp create `
  --name $CONTAINER_APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --environment $CONTAINER_APP_ENV `
  --image "${CONTAINER_REGISTRY}.azurecr.io/${IMAGE_NAME}:latest" `
  --target-port 8000 `
  --ingress 'external' `
  --registry-server "${CONTAINER_REGISTRY}.azurecr.io" `
  --cpu 0.25 `
  --memory 0.5Gi `
  --min-replicas 0 `
  --max-replicas 1 `
  --env-vars "TEAM_TOKEN=$TEAM_TOKEN" "PYTHONPATH=/app"

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "🌐 Your app will be available at:" -ForegroundColor Cyan
az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv
