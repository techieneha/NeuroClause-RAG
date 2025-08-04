# 🚀 NeuroClause-RAG Deployment Guide

## Free Deployment Options

### 🥇 Option 1: Azure Container Apps (Recommended)

**Why Azure Container Apps?**
- ✅ Free tier: 180,000 vCPU-seconds, 360,000 GiB-seconds per month
- ✅ Scales to zero (no cost when not in use)
- ✅ Built-in load balancing and HTTPS
- ✅ Easy to manage and monitor

**Prerequisites:**
1. Install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
2. Create Azure account (free): https://azure.microsoft.com/free/

**Quick Deploy Steps:**

1. **Update your token in deploy script:**
   ```powershell
   # Edit deploy-azure.ps1 and change:
   $TEAM_TOKEN = "your_actual_hackrx_token_here"
   ```

2. **Run deployment (Windows PowerShell):**
   ```powershell
   .\deploy-azure.ps1
   ```

3. **Or manually step by step:**
   ```powershell
   # Login to Azure
   az login
   
   # Install Container Apps extension
   az extension add --name containerapp --upgrade
   
   # Create resource group
   az group create --name neuroclause-rg --location eastus2
   
   # Create container registry
   az acr create --resource-group neuroclause-rg --name neuroclaregistry --sku Basic --admin-enabled true
   
   # Build and push image
   az acr build --registry neuroclaregistry --image neuroclause-rag:latest .
   
   # Create Container Apps environment
   az containerapp env create --name neuroclause-env --resource-group neuroclause-rg --location eastus2
   
   # Deploy app
   az containerapp create --name neuroclause-app --resource-group neuroclause-rg --environment neuroclause-env --image neuroclaregistry.azurecr.io/neuroclause-rag:latest --target-port 8000 --ingress external --cpu 0.25 --memory 0.5Gi --min-replicas 0 --max-replicas 1 --env-vars "TEAM_TOKEN=your_token" "PYTHONPATH=/app"
   ```

### 🥈 Option 2: Railway.app

**Why Railway?**
- ✅ 500 execution hours/month free
- ✅ Super simple deployment
- ✅ Automatic HTTPS and domain

**Steps:**
1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Deploy: `railway deploy`

### 🥉 Option 3: Render.com

**Why Render?**
- ✅ Free tier available
- ✅ Automatic deployments from Git
- ✅ Built-in SSL

You already have `render.yaml` configured! Just:
1. Connect your GitHub repo to Render
2. Deploy automatically

### 🎯 Option 4: Google Cloud Run

**Why Cloud Run?**
- ✅ 2 million requests/month free
- ✅ Scales to zero
- ✅ Fast cold starts

**Steps:**
```bash
# Install gcloud CLI
# gcloud auth login
# gcloud config set project YOUR_PROJECT_ID

# Build and deploy
gcloud run deploy neuroclause-rag --source . --platform managed --region us-central1 --allow-unauthenticated
```

## 📊 Cost Comparison

| Platform | Free Tier | Limitations | Best For |
|----------|-----------|-------------|----------|
| Azure Container Apps | 180k vCPU-sec/month | Scales to 0 | Production-ready apps |
| Railway | 500 hours/month | Always running | Development/testing |
| Render | 750 hours/month | Sleeps after 15min | Side projects |
| Google Cloud Run | 2M requests/month | Pay per request | High traffic |

## 🔧 Environment Variables

Make sure to set these environment variables in your deployment:

```
TEAM_TOKEN=your_hackrx_token_here
PYTHONPATH=/app
```

## 🚨 Important Notes

1. **Model Storage**: Your sentence-transformers model will be downloaded on first run. Consider:
   - Using a persistent volume (Azure Container Apps supports this)
   - Or building the model into your Docker image

2. **Memory Requirements**: Your app might need more than 512MB for ML models. Monitor and adjust as needed.

3. **Cold Starts**: Free tiers often have cold starts. Consider keeping the app warm with a scheduled ping.

4. **Secrets Management**: Use Azure Key Vault or platform-specific secret management for production.

## 📈 Monitoring

After deployment, monitor your app:
- Check logs: `az containerapp logs show --name neuroclause-app --resource-group neuroclause-rg`
- Monitor metrics in Azure portal
- Set up alerts for errors

## 🔄 Updates

To update your deployed app:
```powershell
# Rebuild and redeploy
az acr build --registry neuroclaregistry --image neuroclause-rag:latest .
az containerapp update --name neuroclause-app --resource-group neuroclause-rg --image neuroclaregistry.azurecr.io/neuroclause-rag:latest
```

## 🆘 Troubleshooting

**Common Issues:**
1. **Port binding**: Ensure your app listens on 0.0.0.0, not 127.0.0.1
2. **Health checks**: Make sure `/health` endpoint works
3. **Dependencies**: Check all requirements are in requirements.txt
4. **Environment**: Verify environment variables are set correctly

**Debug Commands:**
```powershell
# Check app status
az containerapp show --name neuroclause-app --resource-group neuroclause-rg

# View logs
az containerapp logs show --name neuroclause-app --resource-group neuroclause-rg --follow

# Scale manually if needed
az containerapp update --name neuroclause-app --resource-group neuroclause-rg --min-replicas 1
```

## 🎉 Success!

Once deployed, your API will be available at:
`https://neuroclause-app.{random-string}.eastus2.azurecontainerapps.io`

Test with:
```bash
curl -X POST "https://your-app-url/api/v1/hackrx/run" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{"documents": "pdf_url", "questions": ["test question"]}'
```
