# 🌟 Deploy NeuroClause-RAG Using Azure Cloud Shell

## Why Azure Cloud Shell?
- ✅ **No installations needed** - Everything is pre-configured
- ✅ **Azure CLI already installed** - Ready to use
- ✅ **Free to use** - Part of your Azure account
- ✅ **Works in any browser** - No local setup required
- ✅ **5GB storage included** - For your files

---

## 📋 Step-by-Step Deployment Guide

### Step 1: Create Azure Account (if not done)
1. Go to: https://azure.microsoft.com/free/
2. Click "Start free" and complete signup
3. You'll get $200 free credit + always-free services

### Step 2: Access Azure Cloud Shell
1. Go to: https://shell.azure.com
2. Sign in with your Azure account
3. Choose **Bash** (recommended) or PowerShell
4. If first time, it will create storage account (free)

### Step 3: Upload Your Project Files

#### Option A: Upload via Cloud Shell Interface
1. Click the **Upload/Download** icon (📁) in Cloud Shell toolbar
2. Select **Upload** 
3. Choose all your project files:
   - `api/` folder
   - `rag_pipeline/` folder
   - `requirements.txt`
   - `Dockerfile`
   - All other project files

#### Option B: Clone from GitHub (if your code is on GitHub)
```bash
# If your code is on GitHub:
git clone https://github.com/techieneha/NeuroClause-RAG.git
cd NeuroClause-RAG
```

#### Option C: Create files manually in Cloud Shell
```bash
# Create project directory
mkdir neuroclause-rag
cd neuroclause-rag

# You can copy-paste file contents using Cloud Shell editor
# Type 'code filename.py' to edit files
```

### Step 4: Set Your Environment Variables
```bash
# Set your variables (update these values)
export RESOURCE_GROUP="neuroclause-rg"
export LOCATION="eastus2"
export CONTAINER_APP_ENV="neuroclause-env"
export CONTAINER_APP_NAME="neuroclause-app"
export CONTAINER_REGISTRY="neuroclaregistry$(shuf -i 1000-9999 -n 1)"
export IMAGE_NAME="neuroclause-rag"
export TEAM_TOKEN="your_hackrx_token_here"  # 🚨 CHANGE THIS!

# Verify variables are set
echo "Registry: $CONTAINER_REGISTRY"
echo "Token: $TEAM_TOKEN"
```

### Step 5: Install Container Apps Extension
```bash
# Install the Azure Container Apps extension
az extension add --name containerapp --upgrade
```

### Step 6: Create Azure Resources
```bash
# 1. Create Resource Group
echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# 2. Create Container Registry (Free Basic tier)
echo "🏗️ Creating Container Registry..."
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $CONTAINER_REGISTRY \
  --sku Basic \
  --admin-enabled true

# 3. Build and Push Docker Image
echo "🐳 Building Docker image..."
az acr build \
  --registry $CONTAINER_REGISTRY \
  --image $IMAGE_NAME:latest \
  .

# 4. Create Container Apps Environment
echo "🌍 Creating Container Apps Environment..."
az containerapp env create \
  --name $CONTAINER_APP_ENV \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

### Step 7: Deploy Your Application
```bash
# Deploy the Container App
echo "🚀 Deploying your NeuroClause-RAG app..."
az containerapp create \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINER_APP_ENV \
  --image $CONTAINER_REGISTRY.azurecr.io/$IMAGE_NAME:latest \
  --target-port 8000 \
  --ingress external \
  --registry-server $CONTAINER_REGISTRY.azurecr.io \
  --cpu 0.25 \
  --memory 0.5Gi \
  --min-replicas 0 \
  --max-replicas 1 \
  --env-vars "TEAM_TOKEN=$TEAM_TOKEN" "PYTHONPATH=/app"
```

### Step 8: Get Your App URL
```bash
# Get the public URL of your deployed app
echo "🌐 Your app is deployed at:"
az containerapp show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  -o tsv
```

---

## 🧪 Test Your Deployed App

### 1. Health Check
```bash
# Save your app URL
APP_URL=$(az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)

# Test health endpoint
curl https://$APP_URL/health
# Should return: {"status":"OK","version":"1.0.0"}
```

### 2. Test API Endpoint
```bash
# Test the main API endpoint
curl -X POST "https://$APP_URL/api/v1/hackrx/run" \
  -H "Authorization: Bearer $TEAM_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://example.com/sample.pdf",
    "questions": ["What is this document about?"]
  }'
```

---

## 📊 Monitor Your Deployment

### Check Application Status
```bash
# View app details
az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP

# Check if app is running
az containerapp revision list --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --output table
```

### View Application Logs
```bash
# Stream live logs
az containerapp logs show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --follow

# View recent logs
az containerapp logs show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --tail 50
```

---

## 🔄 Update Your App

When you need to update your code:

```bash
# 1. Make your code changes in Cloud Shell editor
code api/main.py  # Opens file editor

# 2. Rebuild and redeploy
az acr build --registry $CONTAINER_REGISTRY --image $IMAGE_NAME:latest .

# 3. Update the container app
az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --image $CONTAINER_REGISTRY.azurecr.io/$IMAGE_NAME:latest
```

---

## 🧹 Clean Up Resources (Optional)

To delete everything and stop all charges:

```bash
# Delete the entire resource group (removes everything)
az group delete --name $RESOURCE_GROUP --yes --no-wait

# This will delete:
# - Container App
# - Container Registry  
# - Container Apps Environment
# - All associated resources
```

---

## 🚨 Troubleshooting

### Issue 1: Container Registry Name Taken
```bash
# Generate a new unique name
export CONTAINER_REGISTRY="neuroclaregistry$(shuf -i 1000-9999 -n 1)"
echo "New registry name: $CONTAINER_REGISTRY"
```

### Issue 2: Build Fails
```bash
# Check if Dockerfile exists
ls -la Dockerfile

# View build logs
az acr task logs --registry $CONTAINER_REGISTRY
```

### Issue 3: App Not Starting
```bash
# Check app logs for errors
az containerapp logs show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --tail 100

# Check environment variables
az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query properties.template.containers[0].env
```

### Issue 4: Upload Files to Cloud Shell
```bash
# If upload failed, try creating directories first
mkdir -p api rag_pipeline data

# Then upload files to respective folders
# Use the upload button in Cloud Shell interface
```

---

## 💰 Cost Monitoring

Your app uses Azure's **free tier**:
- **Container Apps**: 180,000 vCPU-seconds/month (free)
- **Container Registry**: 10 GB storage (free)
- **Bandwidth**: 15 GB outbound/month (free)

### Check Usage:
```bash
# View resource usage
az consumption usage list --output table

# Monitor costs
az billing invoice list --output table
```

---

## ✅ Success Checklist

- [ ] Azure account created
- [ ] Accessed Azure Cloud Shell at shell.azure.com
- [ ] Uploaded all project files
- [ ] Set TEAM_TOKEN environment variable
- [ ] Ran all deployment commands successfully
- [ ] Got public URL for your app
- [ ] Tested health endpoint
- [ ] App responds to API calls

---

## 🎉 You're Done!

Your NeuroClause-RAG app is now live on Azure! 

**Your app URL**: `https://neuroclause-app-[random].eastus2.azurecontainerapps.io`

The app will:
- ✅ Scale to zero when not used (no cost)
- ✅ Auto-scale based on traffic
- ✅ Have built-in HTTPS and load balancing
- ✅ Be accessible from anywhere in the world

Need help? The Azure Cloud Shell has built-in documentation: type `az --help` for Azure CLI help!
