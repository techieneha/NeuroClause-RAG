#!/bin/bash

# Azure Container Apps Deployment Script
# This script deploys your NeuroClause-RAG app to Azure Container Apps (Free Tier)

# Variables - Update these
RESOURCE_GROUP="neuroclause-rg"
LOCATION="eastus2"
CONTAINER_APP_ENV="neuroclause-env"
CONTAINER_APP_NAME="neuroclause-app"
CONTAINER_REGISTRY="neuroclaregistry"
IMAGE_NAME="neuroclause-rag"
TEAM_TOKEN="your_hackrx_token_here"  # Replace with your actual token

echo "🚀 Starting Azure Container Apps Deployment..."

# 1. Login to Azure
echo "📝 Logging in to Azure..."
az login

# 2. Create Resource Group
echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# 3. Create Container Registry (Free tier)
echo "🏗️ Creating Container Registry..."
az acr create --resource-group $RESOURCE_GROUP --name $CONTAINER_REGISTRY --sku Basic --admin-enabled true

# 4. Build and push Docker image
echo "🐳 Building and pushing Docker image..."
az acr build --registry $CONTAINER_REGISTRY --image $IMAGE_NAME:latest .

# 5. Create Container Apps Environment
echo "🌍 Creating Container Apps Environment..."
az containerapp env create \
  --name $CONTAINER_APP_ENV \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# 6. Deploy Container App
echo "🚀 Deploying Container App..."
az containerapp create \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINER_APP_ENV \
  --image $CONTAINER_REGISTRY.azurecr.io/$IMAGE_NAME:latest \
  --target-port 8000 \
  --ingress 'external' \
  --registry-server $CONTAINER_REGISTRY.azurecr.io \
  --cpu 0.25 \
  --memory 0.5Gi \
  --min-replicas 0 \
  --max-replicas 1 \
  --env-vars TEAM_TOKEN=$TEAM_TOKEN PYTHONPATH=/app

echo "✅ Deployment complete!"
echo "🌐 Your app will be available at:"
az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv
