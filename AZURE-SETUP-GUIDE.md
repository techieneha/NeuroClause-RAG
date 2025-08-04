# 🌟 Azure Account Setup & Deployment Guide

## Step 1: Create Your Free Azure Account

### 🆓 Azure Free Account Benefits
- **$200 credit** for first 30 days
- **12 months** of popular free services
- **Always free** services (including Container Apps free tier)
- **No automatic charges** after free credit expires

### 📝 Sign Up Process

1. **Go to Azure Portal**: https://azure.microsoft.com/free/
2. **Click "Start free"**
3. **Sign in with Microsoft account** (or create one):
   - Use your existing email (Gmail, Outlook, etc.)
   - Or create a new Microsoft account
4. **Verify your identity**:
   - Phone number verification
   - Credit card verification (for identity only - won't be charged)
5. **Complete profile**:
   - Country/region
   - Basic information
6. **Agreement**: Accept terms and conditions

### ⚠️ Important Notes:
- **Credit card required** for verification but won't be charged
- **No automatic billing** - you control when to upgrade
- **Free services remain free** even after credit expires

## Step 2: Install Azure CLI

### For Windows (PowerShell):
```powershell
# Option 1: Using winget (recommended)
winget install -e --id Microsoft.AzureCLI

# Option 2: Download MSI installer
# Go to: https://aka.ms/installazurecliwindows
```

### Alternative: Use Azure Cloud Shell
- No installation needed
- Access at: https://shell.azure.com
- Pre-installed Azure CLI in browser

## Step 3: First Time Setup

### 1. Login to Azure
```powershell
# Login to your Azure account
az login

# This will open a browser window for authentication
# Sign in with your Azure account credentials
```

### 2. Verify Login
```powershell
# Check your subscriptions
az account list --output table

# Set default subscription (if you have multiple)
az account set --subscription "Your Subscription Name"
```

### 3. Install Container Apps Extension
```powershell
# Install the Container Apps extension
az extension add --name containerapp --upgrade
```

## Step 4: Deploy Your App

### 🚀 Quick Deploy Script

1. **Update your token** in `deploy-azure.ps1`:
   ```powershell
   $TEAM_TOKEN = "your_actual_hackrx_token_here"
   ```

2. **Run the deployment**:
   ```powershell
   # Navigate to your project directory
   cd "c:\Users\pratikshadnyandev.m\Desktop\NeuroClause-RAG"
   
   # Run deployment script
   .\deploy-azure.ps1
   ```

### 📊 What the Script Does:
1. ✅ Creates resource group
2. ✅ Creates container registry (free tier)
3. ✅ Builds Docker image from your code
4. ✅ Creates Container Apps environment
5. ✅ Deploys your app
6. ✅ Provides public URL

## Step 5: Troubleshooting Common Issues

### Issue 1: PowerShell Execution Policy
```powershell
# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 2: Container Registry Name Conflict
```powershell
# If registry name is taken, change it in deploy-azure.ps1:
$CONTAINER_REGISTRY = "neuroclause$(Get-Random -Minimum 1000 -Maximum 9999)"
```

### Issue 3: Resource Name Conflicts
```powershell
# Add random suffix to avoid conflicts:
$RESOURCE_GROUP = "neuroclause-rg-$(Get-Random -Minimum 100 -Maximum 999)"
```

## Step 6: Monitor Your Free Usage

### Check Resource Usage:
1. Go to **Azure Portal**: https://portal.azure.com
2. Navigate to **Cost Management + Billing**
3. Check **Free services** usage
4. Monitor **Container Apps** consumption

### Free Tier Limits:
- **Container Apps**: 180,000 vCPU-seconds/month
- **Container Registry**: 10 GB storage
- **Bandwidth**: 15 GB outbound/month

## 🎯 Alternative: Manual Deployment Steps

If you prefer step-by-step manual deployment:

```powershell
# 1. Login
az login

# 2. Create resource group
az group create --name neuroclause-rg --location eastus2

# 3. Create container registry
az acr create --resource-group neuroclause-rg --name neuroclaregistry --sku Basic --admin-enabled true

# 4. Build image
az acr build --registry neuroclaregistry --image neuroclause-rag:latest .

# 5. Create Container Apps environment
az containerapp env create --name neuroclause-env --resource-group neuroclause-rg --location eastus2

# 6. Deploy app
az containerapp create \
  --name neuroclause-app \
  --resource-group neuroclause-rg \
  --environment neuroclause-env \
  --image neuroclaregistry.azurecr.io/neuroclause-rag:latest \
  --target-port 8000 \
  --ingress external \
  --cpu 0.25 \
  --memory 0.5Gi \
  --min-replicas 0 \
  --max-replicas 1 \
  --env-vars "TEAM_TOKEN=your_token" "PYTHONPATH=/app"
```

## 🚨 Pre-Deployment Checklist

- [ ] Azure account created and verified
- [ ] Azure CLI installed and logged in
- [ ] Updated `TEAM_TOKEN` in deployment script
- [ ] Verified Docker is working (optional - Azure handles this)
- [ ] All files are saved in your project directory

## 📞 Need Help?

### Azure Support:
- **Free support**: Billing and subscription management
- **Documentation**: https://docs.microsoft.com/azure/
- **Community**: https://aka.ms/azurecommunity

### Common Questions:
1. **"Will I be charged?"** - No, with free tier limits
2. **"How to delete resources?"** - Delete the resource group
3. **"App not working?"** - Check logs with deployment script

## 🎉 Success Indicators

After successful deployment, you'll see:
```
✅ Deployment complete!
🌐 Your app will be available at:
https://neuroclause-app.[random].eastus2.azurecontainerapps.io
```

Test your API:
```bash
curl -X GET "https://your-app-url/health"
# Should return: {"status": "OK", "version": "1.0.0"}
```

Ready to start? Let me know when you've created your Azure account and I'll help you with the next steps!
