#!/bin/bash
# Simple Azure deployment for pharmacy PDF processor

# Configuration
RESOURCE_GROUP="pharmchat-rg"
LOCATION="East US"
APP_NAME="pharmacy-pdf-processor"
PLAN_NAME="pharmacy-plan"

echo "🏥 Creating Azure deployment for Pharmacy PDF Processor..."

# Create resource group
echo "Creating resource group: $RESOURCE_GROUP"
az group create --name $RESOURCE_GROUP --location "$LOCATION"

# Create app service plan
echo "Creating app service plan: $PLAN_NAME"
az appservice plan create --name $PLAN_NAME --resource-group $RESOURCE_GROUP --sku B1 --is-linux

# Create web app
echo "Creating web app: $APP_NAME"
az webapp create --resource-group $RESOURCE_GROUP --plan $PLAN_NAME --name $APP_NAME --runtime "PYTHON|3.11"

# Configure startup command
echo "Configuring startup command..."
az webapp config set --name $APP_NAME --resource-group $RESOURCE_GROUP --startup-file "python simple_app.py"

# Deploy the code
echo "Deploying application code..."
zip -r pharmacy-deploy.zip . -x "webapp-logs*" "*.git*" "__pycache__*" "*.pyc"
az webapp deployment source config-zip --name $APP_NAME --resource-group $RESOURCE_GROUP --src pharmacy-deploy.zip

echo "✅ Deployment complete!"
echo "🌐 Your pharmacy app is available at: https://${APP_NAME}.azurewebsites.net"
