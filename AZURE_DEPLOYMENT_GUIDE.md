# Azure Deployment Guide for White Label Chat SaaS

## Overview
This guide will walk you through deploying your white-label chat platform to Microsoft Azure using Azure App Service, Azure Database for PostgreSQL, and Azure Cache for Redis.

## Prerequisites

1. **Azure Account**: Sign up at [portal.azure.com](https://portal.azure.com)
2. **Azure CLI**: Install from [docs.microsoft.com/cli/azure/install-azure-cli](https://docs.microsoft.com/cli/azure/install-azure-cli)
3. **Docker** (for container deployment option)
4. **Git** for source code deployment

## Deployment Options

### Option 1: Azure App Service (Recommended)
- **Best for**: Quick deployment with managed infrastructure
- **Scaling**: Automatic scaling available
- **Cost**: Pay-as-you-scale model

### Option 2: Azure Container Instances
- **Best for**: Containerized deployment with full control
- **Scaling**: Manual scaling with container groups
- **Cost**: Pay per container runtime

### Option 3: Azure Kubernetes Service (AKS)
- **Best for**: Enterprise-scale with high availability
- **Scaling**: Advanced orchestration and auto-scaling
- **Cost**: Higher cost but maximum flexibility

## Option 1: Azure App Service Deployment (Recommended)

### Step 1: Install Azure CLI and Login

```bash
# Install Azure CLI (Windows)
winget install Microsoft.AzureCLI

# Login to Azure
az login

# Set your subscription (if you have multiple)
az account list
az account set --subscription "your-subscription-id"
```

### Step 2: Create Resource Group

```bash
# Create a resource group
az group create --name white-label-rg --location "East US"
```

### Step 3: Create Azure Database for PostgreSQL

```bash
# Create PostgreSQL server
az postgres flexible-server create \
  --resource-group white-label-rg \
  --name white-label-db-server \
  --location "East US" \
  --admin-user dbadmin \
  --admin-password "YourSecurePassword123!" \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --version 15

# Create database
az postgres flexible-server db create \
  --resource-group white-label-rg \
  --server-name white-label-db-server \
  --database-name whitelabel_chat

# Configure firewall to allow Azure services
az postgres flexible-server firewall-rule create \
  --resource-group white-label-rg \
  --name white-label-db-server \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

### Step 4: Create Azure Cache for Redis

```bash
# Create Redis cache
az redis create \
  --resource-group white-label-rg \
  --name white-label-redis \
  --location "East US" \
  --sku Basic \
  --vm-size c0
```

### Step 5: Create App Service Plan and Web App

```bash
# Create App Service plan
az appservice plan create \
  --resource-group white-label-rg \
  --name white-label-plan \
  --location "East US" \
  --sku B1 \
  --is-linux

# Create Web App
az webapp create \
  --resource-group white-label-rg \
  --plan white-label-plan \
  --name white-label-chat-app \
  --runtime "PYTHON:3.11"
```

### Step 6: Configure Environment Variables

```bash
# Get database connection string
DB_HOST=$(az postgres flexible-server show --resource-group white-label-rg --name white-label-db-server --query "fullyQualifiedDomainName" -o tsv)

# Get Redis connection details
REDIS_HOST=$(az redis show --resource-group white-label-rg --name white-label-redis --query "hostName" -o tsv)
REDIS_KEY=$(az redis list-keys --resource-group white-label-rg --name white-label-redis --query "primaryKey" -o tsv)

# Set environment variables
az webapp config appsettings set \
  --resource-group white-label-rg \
  --name white-label-chat-app \
  --settings \
    FLASK_ENV=production \
    SECRET_KEY="your-secret-key-here" \
    DATABASE_URL="postgresql://dbadmin:YourSecurePassword123!@${DB_HOST}:5432/whitelabel_chat?sslmode=require" \
    REDIS_URL="redis://:${REDIS_KEY}@${REDIS_HOST}:6380/0?ssl_cert_reqs=required" \
    MAIL_SERVER="smtp.sendgrid.net" \
    MAIL_PORT=587 \
    MAIL_USE_TLS=True \
    MAIL_USERNAME="apikey" \
    MAIL_PASSWORD="your-sendgrid-api-key"
```

### Step 7: Deploy Application

```bash
# Deploy from local Git repository
az webapp deployment source config-local-git \
  --resource-group white-label-rg \
  --name white-label-chat-app

# Get deployment URL
DEPLOY_URL=$(az webapp deployment list-publishing-credentials --resource-group white-label-rg --name white-label-chat-app --query "scmUri" -o tsv)

# Add Azure remote and deploy
git remote add azure $DEPLOY_URL
git push azure main
```

## Option 2: Azure Container Instances

### Step 1: Build and Push Docker Image

```bash
# Build Docker image
docker build -f Dockerfile.prod -t white-label-chat .

# Tag for Azure Container Registry
docker tag white-label-chat whitelabelacr.azurecr.io/white-label-chat:latest

# Create Azure Container Registry
az acr create \
  --resource-group white-label-rg \
  --name whitelabelacr \
  --sku Basic \
  --admin-enabled true

# Login to ACR
az acr login --name whitelabelacr

# Push image
docker push whitelabelacr.azurecr.io/white-label-chat:latest
```

### Step 2: Deploy Container

```bash
# Get ACR credentials
ACR_PASSWORD=$(az acr credential show --name whitelabelacr --query "passwords[0].value" -o tsv)

# Create container instance
az container create \
  --resource-group white-label-rg \
  --name white-label-chat-container \
  --image whitelabelacr.azurecr.io/white-label-chat:latest \
  --registry-login-server whitelabelacr.azurecr.io \
  --registry-username whitelabelacr \
  --registry-password $ACR_PASSWORD \
  --dns-name-label white-label-chat \
  --ports 5000 \
  --environment-variables \
    FLASK_ENV=production \
    SECRET_KEY="your-secret-key" \
    DATABASE_URL="your-database-url" \
    REDIS_URL="your-redis-url"
```

## Option 3: Azure Kubernetes Service (AKS)

### Step 1: Create AKS Cluster

```bash
# Create AKS cluster
az aks create \
  --resource-group white-label-rg \
  --name white-label-aks \
  --node-count 2 \
  --node-vm-size Standard_B2s \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group white-label-rg --name white-label-aks
```

### Step 2: Deploy to Kubernetes

Create `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: white-label-chat
spec:
  replicas: 3
  selector:
    matchLabels:
      app: white-label-chat
  template:
    metadata:
      labels:
        app: white-label-chat
    spec:
      containers:
      - name: white-label-chat
        image: whitelabelacr.azurecr.io/white-label-chat:latest
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
        - name: DATABASE_URL
          value: "your-database-url"
        - name: REDIS_URL
          value: "your-redis-url"
---
apiVersion: v1
kind: Service
metadata:
  name: white-label-chat-service
spec:
  selector:
    app: white-label-chat
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
```

Deploy:
```bash
kubectl apply -f k8s-deployment.yaml
```

## Security Configuration

### 1. Enable HTTPS

```bash
# For App Service - custom domain with SSL
az webapp config ssl bind \
  --resource-group white-label-rg \
  --name white-label-chat-app \
  --certificate-thumbprint your-cert-thumbprint \
  --ssl-type SNI
```

### 2. Configure Firewall Rules

```bash
# Restrict database access to App Service
az postgres flexible-server firewall-rule create \
  --resource-group white-label-rg \
  --name white-label-db-server \
  --rule-name AllowAppService \
  --start-ip-address your-app-service-ip \
  --end-ip-address your-app-service-ip
```

### 3. Enable Application Insights

```bash
# Create Application Insights
az monitor app-insights component create \
  --resource-group white-label-rg \
  --app white-label-insights \
  --location "East US" \
  --application-type web

# Get instrumentation key
INSIGHTS_KEY=$(az monitor app-insights component show --resource-group white-label-rg --app white-label-insights --query "instrumentationKey" -o tsv)

# Add to app settings
az webapp config appsettings set \
  --resource-group white-label-rg \
  --name white-label-chat-app \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY=$INSIGHTS_KEY
```

## Monitoring and Scaling

### 1. Auto-scaling

```bash
# Configure auto-scaling rules
az monitor autoscale create \
  --resource-group white-label-rg \
  --resource white-label-plan \
  --resource-type Microsoft.Web/serverfarms \
  --name white-label-autoscale \
  --min-count 1 \
  --max-count 10 \
  --count 2

# Add CPU-based scaling rule
az monitor autoscale rule create \
  --resource-group white-label-rg \
  --autoscale-name white-label-autoscale \
  --condition "Percentage CPU > 70 avg 5m" \
  --scale out 2
```

### 2. Health Checks

```bash
# Configure health check endpoint
az webapp config set \
  --resource-group white-label-rg \
  --name white-label-chat-app \
  --health-check-path "/api/health"
```

## Cost Optimization

### 1. Development Environment

```bash
# Create smaller resources for development
az appservice plan create \
  --resource-group white-label-dev-rg \
  --name white-label-dev-plan \
  --sku F1 \
  --is-linux

az postgres flexible-server create \
  --resource-group white-label-dev-rg \
  --name white-label-dev-db \
  --sku-name Standard_B1ms \
  --tier Burstable
```

### 2. Production Scaling

```bash
# Scale up for production
az appservice plan update \
  --resource-group white-label-rg \
  --name white-label-plan \
  --sku P1v2

az postgres flexible-server update \
  --resource-group white-label-rg \
  --name white-label-db-server \
  --sku-name Standard_D2s_v3 \
  --tier GeneralPurpose
```

## Backup and Disaster Recovery

### 1. Database Backups

```bash
# Configure automated backups
az postgres flexible-server parameter set \
  --resource-group white-label-rg \
  --server-name white-label-db-server \
  --name backup_retention_days \
  --value 30
```

### 2. App Service Backups

```bash
# Create storage account for backups
az storage account create \
  --resource-group white-label-rg \
  --name whitelabelbackups \
  --sku Standard_LRS

# Configure backup
az webapp config backup update \
  --resource-group white-label-rg \
  --webapp-name white-label-chat-app \
  --container-url "your-storage-container-url" \
  --frequency 1 \
  --retain-one true \
  --retention 30
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check firewall rules
   - Verify connection string format
   - Ensure SSL is properly configured

2. **App Service Deployment Failures**
   - Check application logs: `az webapp log tail`
   - Verify Python version compatibility
   - Check startup command configuration

3. **Performance Issues**
   - Monitor with Application Insights
   - Check auto-scaling rules
   - Optimize database queries

### Useful Commands

```bash
# View application logs
az webapp log tail --resource-group white-label-rg --name white-label-chat-app

# SSH into App Service
az webapp ssh --resource-group white-label-rg --name white-label-chat-app

# Check resource usage
az monitor metrics list --resource-group white-label-rg --resource white-label-chat-app

# Scale manually
az appservice plan update --resource-group white-label-rg --name white-label-plan --number-of-workers 3
```

## Next Steps

1. **Custom Domain**: Configure your custom domain and SSL certificate
2. **CDN**: Set up Azure CDN for static assets
3. **API Management**: Add Azure API Management for advanced API features
4. **DevOps**: Set up Azure DevOps for CI/CD pipelines
5. **Monitoring**: Configure alerts and dashboards in Azure Monitor

## Cost Estimation

### Minimum Production Setup:
- **App Service Plan (B1)**: ~$13/month
- **PostgreSQL Flexible Server (B1ms)**: ~$12/month
- **Redis Cache (Basic C0)**: ~$17/month
- **Application Insights**: ~$2/month (for basic usage)
- **Total**: ~$44/month

### Recommended Production Setup:
- **App Service Plan (P1v2)**: ~$73/month
- **PostgreSQL Flexible Server (D2s_v3)**: ~$50/month
- **Redis Cache (Standard C1)**: ~$55/month
- **Application Insights**: ~$5/month
- **Total**: ~$183/month

Costs can be reduced with Azure Reserved Instances and proper resource sizing based on actual usage.
