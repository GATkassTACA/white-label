#!/bin/bash

# Azure Deployment Script for White Label Chat SaaS
# This script automates the deployment to Azure App Service

set -e

echo "🚀 Starting Azure deployment for White Label Chat SaaS..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RESOURCE_GROUP="white-label-rg"
LOCATION="East US"
APP_NAME="white-label-chat-app"
PLAN_NAME="white-label-plan"
DB_SERVER_NAME="white-label-db-server"
REDIS_NAME="white-label-redis"
ACR_NAME="whitelabelacr"
DB_ADMIN_USER="dbadmin"
DB_NAME="whitelabel_chat"
INSIGHTS_NAME="white-label-insights"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed. Please install it first:"
    echo "https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if user is logged in to Azure
if ! az account show &> /dev/null; then
    print_warning "You are not logged in to Azure. Please login first."
    az login
fi

# Get current subscription
SUBSCRIPTION=$(az account show --query "name" -o tsv)
print_status "Using subscription: $SUBSCRIPTION"

# Ask for confirmation
read -p "Do you want to continue with the deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Deployment cancelled."
    exit 0
fi

# Generate secure passwords
print_status "Generating secure passwords..."
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

print_success "Generated secure passwords"

# Create resource group
print_status "Creating resource group: $RESOURCE_GROUP"
az group create --name $RESOURCE_GROUP --location "$LOCATION" --output none
print_success "Resource group created"

# Create PostgreSQL server
print_status "Creating PostgreSQL server: $DB_SERVER_NAME"
az postgres flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name $DB_SERVER_NAME \
  --location "$LOCATION" \
  --admin-user $DB_ADMIN_USER \
  --admin-password "$DB_PASSWORD" \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --version 15 \
  --storage-size 32 \
  --output none

print_success "PostgreSQL server created"

# Create database
print_status "Creating database: $DB_NAME"
az postgres flexible-server db create \
  --resource-group $RESOURCE_GROUP \
  --server-name $DB_SERVER_NAME \
  --database-name $DB_NAME \
  --output none

print_success "Database created"

# Configure firewall for Azure services
print_status "Configuring database firewall rules"
az postgres flexible-server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --name $DB_SERVER_NAME \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0 \
  --output none

print_success "Database firewall configured"

# Create Redis cache
print_status "Creating Redis cache: $REDIS_NAME"
az redis create \
  --resource-group $RESOURCE_GROUP \
  --name $REDIS_NAME \
  --location "$LOCATION" \
  --sku Basic \
  --vm-size c0 \
  --output none

print_success "Redis cache created"

# Create App Service plan
print_status "Creating App Service plan: $PLAN_NAME"
az appservice plan create \
  --resource-group $RESOURCE_GROUP \
  --name $PLAN_NAME \
  --location "$LOCATION" \
  --sku B1 \
  --is-linux \
  --output none

print_success "App Service plan created"

# Create Web App
print_status "Creating Web App: $APP_NAME"
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan $PLAN_NAME \
  --name $APP_NAME \
  --runtime "PYTHON:3.11" \
  --output none

print_success "Web App created"

# Create Application Insights
print_status "Creating Application Insights: $INSIGHTS_NAME"
az monitor app-insights component create \
  --resource-group $RESOURCE_GROUP \
  --app $INSIGHTS_NAME \
  --location "$LOCATION" \
  --application-type web \
  --output none

print_success "Application Insights created"

# Get connection strings and keys
print_status "Retrieving connection strings and keys..."

DB_HOST=$(az postgres flexible-server show --resource-group $RESOURCE_GROUP --name $DB_SERVER_NAME --query "fullyQualifiedDomainName" -o tsv)
REDIS_HOST=$(az redis show --resource-group $RESOURCE_GROUP --name $REDIS_NAME --query "hostName" -o tsv)
REDIS_KEY=$(az redis list-keys --resource-group $RESOURCE_GROUP --name $REDIS_NAME --query "primaryKey" -o tsv)
INSIGHTS_KEY=$(az monitor app-insights component show --resource-group $RESOURCE_GROUP --app $INSIGHTS_NAME --query "instrumentationKey" -o tsv)

print_success "Retrieved connection details"

# Configure app settings
print_status "Configuring application settings..."

DATABASE_URL="postgresql://${DB_ADMIN_USER}:${DB_PASSWORD}@${DB_HOST}:5432/${DB_NAME}?sslmode=require"
REDIS_URL="redis://:${REDIS_KEY}@${REDIS_HOST}:6380/0?ssl_cert_reqs=required"

az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --settings \
    FLASK_ENV=production \
    SECRET_KEY="$SECRET_KEY" \
    DATABASE_URL="$DATABASE_URL" \
    REDIS_URL="$REDIS_URL" \
    APPINSIGHTS_INSTRUMENTATIONKEY="$INSIGHTS_KEY" \
    WEBSITES_PORT=5000 \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    MAIL_SERVER="smtp.sendgrid.net" \
    MAIL_PORT=587 \
    MAIL_USE_TLS=True \
    WTF_CSRF_ENABLED=True \
    SESSION_COOKIE_SECURE=True \
    SESSION_COOKIE_HTTPONLY=True \
    FORCE_HTTPS=True \
  --output none

print_success "Application settings configured"

# Configure startup command
print_status "Configuring startup command..."
az webapp config set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --startup-file "gunicorn --bind 0.0.0.0:5000 app:app" \
  --output none

print_success "Startup command configured"

# Configure health check
print_status "Configuring health check..."
az webapp config set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --health-check-path "/api/health" \
  --output none

print_success "Health check configured"

# Set up local Git deployment
print_status "Setting up Git deployment..."
DEPLOY_URL=$(az webapp deployment source config-local-git \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --query "url" -o tsv)

print_success "Git deployment configured"

# Create environment file
print_status "Creating local environment file..."
cat > .env.azure << EOF
# Azure Environment Configuration
FLASK_ENV=production
SECRET_KEY=$SECRET_KEY
DATABASE_URL=$DATABASE_URL
REDIS_URL=$REDIS_URL
APPINSIGHTS_INSTRUMENTATIONKEY=$INSIGHTS_KEY

# Database Admin Credentials (for backup purposes)
DB_ADMIN_USER=$DB_ADMIN_USER
DB_ADMIN_PASSWORD=$DB_PASSWORD
DB_HOST=$DB_HOST
DB_NAME=$DB_NAME

# Redis Details
REDIS_HOST=$REDIS_HOST
REDIS_KEY=$REDIS_KEY

# Azure Resource Details
RESOURCE_GROUP=$RESOURCE_GROUP
APP_NAME=$APP_NAME
EOF

print_success "Environment file created: .env.azure"

# Add Azure remote if it doesn't exist
if ! git remote get-url azure &> /dev/null; then
    print_status "Adding Azure Git remote..."
    git remote add azure "$DEPLOY_URL"
    print_success "Azure remote added"
else
    print_warning "Azure remote already exists"
fi

# Deploy to Azure
print_status "Deploying application to Azure..."
echo "This may take several minutes..."

if git push azure main; then
    print_success "Application deployed successfully!"
else
    print_error "Deployment failed. Check the output above for errors."
    exit 1
fi

# Get the app URL
APP_URL="https://${APP_NAME}.azurewebsites.net"

# Wait for deployment to complete
print_status "Waiting for application to start..."
sleep 30

# Test health endpoint
print_status "Testing health endpoint..."
if curl -f "$APP_URL/api/health" &> /dev/null; then
    print_success "Health check passed!"
else
    print_warning "Health check failed. The app might still be starting up."
fi

# Display deployment summary
echo
echo "🎉 Deployment completed successfully!"
echo
echo "📋 Deployment Summary:"
echo "===================="
echo "Resource Group: $RESOURCE_GROUP"
echo "App Service: $APP_NAME"
echo "Database Server: $DB_SERVER_NAME"
echo "Redis Cache: $REDIS_NAME"
echo "Application URL: $APP_URL"
echo "Health Check: $APP_URL/api/health"
echo
echo "📁 Configuration files created:"
echo "- .env.azure (contains all connection details)"
echo
echo "🔑 Important Security Notes:"
echo "- Database password: $DB_PASSWORD (saved in .env.azure)"
echo "- Secret key generated and configured"
echo "- Redis access key configured"
echo "- HTTPS is enforced"
echo
echo "📊 Monitoring:"
echo "- Application Insights: https://portal.azure.com/#resource/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Insights/components/$INSIGHTS_NAME"
echo "- App Service logs: az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME"
echo
echo "🛠 Next Steps:"
echo "1. Configure your custom domain and SSL certificate"
echo "2. Set up your email provider (SendGrid) API key"
echo "3. Configure OAuth providers if needed"
echo "4. Set up monitoring alerts"
echo "5. Test all functionality"
echo
print_success "Azure deployment script completed!"
