#!/bin/bash

# InktelliAssist Pro Linux/macOS Deployment Script
# Professional AI Document Processing for Tattoo Parlors

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Default parameters
RESOURCE_GROUP_NAME="InktelliAssist-RG"
LOCATION="East US"
APP_SERVICE_NAME="inktelliassist-pro"
DATABASE_SERVER_NAME="inktelliassist-server-$RANDOM"
DATABASE_NAME="inktelliassist-db"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -g|--resource-group)
            RESOURCE_GROUP_NAME="$2"
            shift 2
            ;;
        -l|--location)
            LOCATION="$2"
            shift 2
            ;;
        -a|--app-name)
            APP_SERVICE_NAME="$2"
            shift 2
            ;;
        -d|--database-server)
            DATABASE_SERVER_NAME="$2"
            shift 2
            ;;
        -h|--help)
            echo "InktelliAssist Pro Deployment Script"
            echo ""
            echo "Options:"
            echo "  -g, --resource-group    Azure Resource Group name (default: InktelliAssist-RG)"
            echo "  -l, --location          Azure region (default: East US)"
            echo "  -a, --app-name          App Service name (default: inktelliassist-pro)"
            echo "  -d, --database-server   Database server name (default: auto-generated)"
            echo "  -h, --help              Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo -e "${MAGENTA}🎨 INKTELLIASSIST PRO DEPLOYMENT${NC}"
echo -e "${CYAN}Professional Intelligence for Ink Artists${NC}"
echo -e "${MAGENTA}======================================${NC}"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI not found. Please install Azure CLI first.${NC}"
    echo "Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

echo -e "${GREEN}✅ Azure CLI detected${NC}"

# Login to Azure
echo -e "${YELLOW}🔐 Logging into Azure...${NC}"
az login

# Set subscription (optional - will use default)
subscription=$(az account show --query "name" -o tsv)
echo -e "${CYAN}📋 Using subscription: $subscription${NC}"

# Create Resource Group
echo -e "${YELLOW}📦 Creating Resource Group: $RESOURCE_GROUP_NAME${NC}"
az group create --name "$RESOURCE_GROUP_NAME" --location "$LOCATION"

# Create App Service Plan
echo -e "${YELLOW}🚀 Creating App Service Plan...${NC}"
az appservice plan create \
    --name "$APP_SERVICE_NAME-plan" \
    --resource-group "$RESOURCE_GROUP_NAME" \
    --location "$LOCATION" \
    --sku B1 \
    --is-linux

# Generate secure password
admin_password=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-16)
admin_user="inktelliassist_admin"

# Create PostgreSQL Server
echo -e "${YELLOW}🗄️ Creating PostgreSQL Server: $DATABASE_SERVER_NAME${NC}"
az postgres flexible-server create \
    --name "$DATABASE_SERVER_NAME" \
    --resource-group "$RESOURCE_GROUP_NAME" \
    --location "$LOCATION" \
    --admin-user "$admin_user" \
    --admin-password "$admin_password" \
    --sku-name Standard_B1ms \
    --tier Burstable \
    --storage-size 32 \
    --version 13

# Create Database
echo -e "${YELLOW}📊 Creating Database: $DATABASE_NAME${NC}"
az postgres flexible-server db create \
    --resource-group "$RESOURCE_GROUP_NAME" \
    --server-name "$DATABASE_SERVER_NAME" \
    --database-name "$DATABASE_NAME"

# Configure Firewall (allow Azure services)
echo -e "${YELLOW}🔥 Configuring Firewall...${NC}"
az postgres flexible-server firewall-rule create \
    --resource-group "$RESOURCE_GROUP_NAME" \
    --name "$DATABASE_SERVER_NAME" \
    --rule-name "AllowAzureServices" \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0

# Create Web App
echo -e "${YELLOW}🌐 Creating Web App: $APP_SERVICE_NAME${NC}"
az webapp create \
    --name "$APP_SERVICE_NAME" \
    --resource-group "$RESOURCE_GROUP_NAME" \
    --plan "$APP_SERVICE_NAME-plan" \
    --runtime "PYTHON|3.9"

# Get database connection details
server_fqdn=$(az postgres flexible-server show \
    --resource-group "$RESOURCE_GROUP_NAME" \
    --name "$DATABASE_SERVER_NAME" \
    --query "fullyQualifiedDomainName" -o tsv)

# Configure App Settings
echo -e "${YELLOW}⚙️ Configuring Application Settings...${NC}"
az webapp config appsettings set \
    --resource-group "$RESOURCE_GROUP_NAME" \
    --name "$APP_SERVICE_NAME" \
    --settings \
        "DATABASE_HOST=$server_fqdn" \
        "DATABASE_NAME=$DATABASE_NAME" \
        "DATABASE_USER=$admin_user" \
        "DATABASE_PASSWORD=$admin_password" \
        "FLASK_ENV=production" \
        "APP_NAME=InktelliAssist Pro" \
        "BRAND_COLOR=#000000" \
        "ACCENT_COLOR=#DC143C" \
        "HIGHLIGHT_COLOR=#00BFFF" \
        "SCM_DO_BUILD_DURING_DEPLOYMENT=true"

echo ""
echo -e "${MAGENTA}🎯 DEPLOYMENT SUMMARY${NC}"
echo -e "${MAGENTA}===================${NC}"
echo -e "${WHITE}Resource Group: $RESOURCE_GROUP_NAME${NC}"
echo -e "${WHITE}App Service: $APP_SERVICE_NAME${NC}"
echo -e "${WHITE}Database Server: $DATABASE_SERVER_NAME${NC}"
echo -e "${WHITE}Database: $DATABASE_NAME${NC}"
echo -e "${WHITE}Admin User: $admin_user${NC}"
echo -e "${YELLOW}Admin Password: $admin_password${NC}"
echo ""
echo -e "${GREEN}🌐 Application URL: https://$APP_SERVICE_NAME.azurewebsites.net${NC}"
echo ""
echo -e "${CYAN}📝 NEXT STEPS:${NC}"
echo -e "${WHITE}1. Deploy the application code using Git or ZIP deployment${NC}"
echo -e "${WHITE}2. Test the application at the URL above${NC}"
echo -e "${WHITE}3. Create admin user account${NC}"
echo -e "${WHITE}4. Configure custom domain (optional)${NC}"
echo ""

# Save credentials to file
credentials_file="inktelliassist-credentials.txt"
cat > "$credentials_file" << EOF
InktelliAssist Pro Deployment Credentials
=========================================
Date: $(date)
Resource Group: $RESOURCE_GROUP_NAME
App Service: $APP_SERVICE_NAME
Database Server: $DATABASE_SERVER_NAME
Database Name: $DATABASE_NAME
Admin User: $admin_user
Admin Password: $admin_password
Connection String: postgresql://$admin_user:$admin_password@$server_fqdn/$DATABASE_NAME
Application URL: https://$APP_SERVICE_NAME.azurewebsites.net

SAVE THIS FILE SECURELY!
EOF

echo -e "${GREEN}💾 Credentials saved to: $credentials_file${NC}"
echo -e "${RED}⚠️  IMPORTANT: Save this file securely and delete from this location!${NC}"
