# Azure DevOps Guide for NeuroClause-RAG

This guide walks you through setting up Azure DevOps pipelines for the NeuroClause-RAG application, including the template evaluation process and deployment configurations.

## Overview

The Azure DevOps pipeline configuration is based on template evaluation that resolves checkout options and deployment steps. The pipeline includes:

- **Automated builds** on code changes
- **Testing** with pytest and custom test scripts
- **Docker image building**
- **Deployment** to Azure Container Apps
- **Template-based configuration** with proper checkout settings

## Template Evaluation Results

The pipeline uses Azure DevOps template evaluation to determine the final configuration. Here's what the template evaluation process reveals:

### Checkout Configuration
```yaml
# Template evaluation result:
steps:
- task: 6d15af64-176c-496d-b583-fd2ae21d4df4@1
  inputs:
    repository: self
    fetchDepth: 1
```

**Key Points:**
- **Task ID**: `6d15af64-176c-496d-b583-fd2ae21d4df4@1` (Azure DevOps Checkout task)
- **Repository**: `self` (current repository)
- **Fetch Depth**: `1` (shallow clone for faster builds)
- **Max Concurrency**: `0` (unlimited parallel operations)

### Template Evaluation Process

The template evaluation checks several conditions:
1. **Job steps validation**: Ensures proper task configuration
2. **Checkout options**: Configures repository fetch settings
3. **Variable resolution**: Resolves dynamic values at runtime

## Pipeline Configuration

### 1. Triggers
- **Branch triggers**: `main` and `azure-setup` branches
- **Pull Request triggers**: Into `main` branch
- **Path exclusions**: Ignores documentation changes

### 2. Variables
```yaml
variables:
  - name: pythonVersion
    value: '3.11'
  - name: vmImageName
    value: 'ubuntu-latest'
  - name: azureServiceConnection
    value: 'NeuroClause-ServiceConnection'
  - name: containerAppName
    value: 'neuroclause-rag'
  - name: resourceGroupName
    value: 'neuroclause-rg'
```

### 3. Build Stage
- **Python setup**: Python 3.11
- **Dependency installation**: pip install from requirements.txt
- **Testing**: pytest and custom test execution
- **Docker build**: Multi-tag container image

### 4. Deploy Stage
- **Conditional deployment**: Only on main branch success
- **Azure Container Apps**: Using PowerShell deployment script
- **Verification**: Post-deployment health checks

## Setup Instructions

### 1. Azure DevOps Project Setup

1. **Create Azure DevOps Project**:
   ```bash
   # Navigate to https://dev.azure.com
   # Create new project: "NeuroClause-RAG"
   ```

2. **Import Repository**:
   ```bash
   # In Azure DevOps, go to Repos > Import repository
   # Clone URL: your-github-repo-url
   ```

### 2. Service Connection Configuration

1. **Create Azure Service Connection**:
   ```bash
   # Project Settings > Service connections
   # New service connection > Azure Resource Manager
   # Service principal (automatic)
   # Name: NeuroClause-ServiceConnection
   ```

2. **Grant Permissions**:
   ```bash
   # Azure Portal > Subscriptions > Access control (IAM)
   # Add role assignment: Contributor
   # Assign to: Azure DevOps service principal
   ```

### 3. Pipeline Creation

1. **Create Pipeline**:
   ```bash
   # Pipelines > New pipeline
   # Azure Repos Git
   # Select repository: NeuroClause-RAG
   # Existing Azure Pipelines YAML file
   # Path: /azure-pipelines.yml
   ```

2. **Configure Variables**:
   ```bash
   # Pipeline > Edit > Variables
   # Add variables as needed for your environment
   ```

### 4. Environment Setup

1. **Create Environment**:
   ```bash
   # Pipelines > Environments
   # New environment: "production"
   # Add resource: None (for now)
   ```

2. **Configure Approvals** (Optional):
   ```bash
   # Environment > production > Approvals and checks
   # Add required approvers for production deployments
   ```

## Azure Resource Setup

### 1. Resource Group
```bash
# Create resource group
az group create --name neuroclause-rg --location eastus
```

### 2. Container Apps Environment
```bash
# Create Container Apps environment
az containerapp env create \
  --name neuroclause-env \
  --resource-group neuroclause-rg \
  --location eastus
```

### 3. Container App
```bash
# Deploy initial container app (will be updated by pipeline)
az containerapp create \
  --name neuroclause-rag \
  --resource-group neuroclause-rg \
  --environment neuroclause-env \
  --image mcr.microsoft.com/azuredocs/containerapps-helloworld:latest \
  --target-port 8000 \
  --ingress 'external'
```

## Deployment Scripts

The pipeline uses the existing deployment scripts:

### PowerShell Script (`deploy-azure.ps1`)
- Handles Azure Container Apps deployment
- Manages environment variables and secrets
- Provides error handling and logging

### Bash Script (`deploy-azure.sh`)
- Alternative deployment option
- Cross-platform compatibility
- Azure CLI commands

## Template Evaluation Deep Dive

### Understanding the Output

The template evaluation output you provided shows:

```
Result: True
Evaluating: not(containsValue(job['steps']['*']['task']['id'], '6d15af64-176c-496d-b583-fd2ae21d4df4'))
```

This indicates:
- **Condition evaluation**: Checking if the checkout task is NOT already present
- **Task validation**: Ensuring proper task configuration
- **Dynamic resolution**: Template variables resolved at runtime

### Checkout Task Details

The checkout task (`6d15af64-176c-496d-b583-fd2ae21d4df4@1`) is the Azure DevOps built-in task for repository checkout with:

- **Shallow clone**: `fetchDepth: 1` for faster builds
- **Self repository**: Uses the current repository
- **Optimized performance**: Minimal data transfer

## Monitoring and Troubleshooting

### 1. Pipeline Monitoring
```bash
# View pipeline runs
# Pipelines > Recent runs
# Check build logs and test results
```

### 2. Deployment Verification
```bash
# Check Azure Container Apps status
az containerapp show \
  --name neuroclause-rag \
  --resource-group neuroclause-rg \
  --query "properties.latestRevisionFqdn"
```

### 3. Common Issues

1. **Service Connection Issues**:
   - Verify Azure subscription permissions
   - Check service principal credentials
   - Validate resource group access

2. **Build Failures**:
   - Check Python version compatibility
   - Verify requirements.txt dependencies
   - Review test execution logs

3. **Deployment Issues**:
   - Validate Azure resource existence
   - Check deployment script permissions
   - Review Container Apps configuration

## Best Practices

### 1. Security
- Use service connections for Azure authentication
- Store secrets in Azure Key Vault
- Limit pipeline permissions to minimum required

### 2. Performance
- Use shallow clones (`fetchDepth: 1`)
- Cache dependencies when possible
- Optimize Docker image layers

### 3. Reliability
- Implement proper error handling
- Add deployment verification steps
- Configure environment-specific approvals

## Next Steps

1. **Set up monitoring**: Application Insights integration
2. **Configure scaling**: Auto-scaling rules for Container Apps
3. **Implement staging**: Additional deployment environments
4. **Add security scanning**: Container vulnerability scans
5. **Optimize builds**: Parallel job execution and caching

## Related Files

- `azure-pipelines.yml`: Main pipeline configuration
- `deploy-azure.ps1`: PowerShell deployment script
- `deploy-azure.sh`: Bash deployment script
- `azure-container-app.yaml`: Container Apps configuration
- `Dockerfile`: Container image definition

For more detailed Azure setup information, see:
- `AZURE-SETUP-GUIDE.md`: Azure resource configuration
- `AZURE-CLOUD-SHELL-GUIDE.md`: Cloud Shell usage
- `DEPLOYMENT.md`: General deployment information
