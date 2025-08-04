#!/bin/bash

# PharmAssist Azure Deployment Script
# Uses ARM templates for consistent, repeatable deployments

set -e

echo "🏥 PharmAssist Azure Deployment"
echo "=================================="

# Configuration
RESOURCE_GROUP="pharmassist-production"
LOCATION="Central US"
TEMPLATE_FILE="pharmassist-deployment-template.json"
PARAMETERS_FILE="pharmassist-deployment-parameters.json"
DEPLOYMENT_NAME="pharmassist-$(date +%Y%m%d-%H%M%S)"

# Create resource group
echo "📁 Creating resource group: $RESOURCE_GROUP"
az group create \
    --name "$RESOURCE_GROUP" \
    --location "$LOCATION"

# Deploy ARM template
echo "🚀 Deploying PharmAssist application..."
DEPLOYMENT_OUTPUT=$(az deployment group create \
    --resource-group "$RESOURCE_GROUP" \
    --template-file "$TEMPLATE_FILE" \
    --parameters "@$PARAMETERS_FILE" \
    --name "$DEPLOYMENT_NAME" \
    --output json)

# Extract outputs
WEB_APP_NAME=$(echo $DEPLOYMENT_OUTPUT | jq -r '.properties.outputs.webAppName.value')
WEB_APP_URL=$(echo $DEPLOYMENT_OUTPUT | jq -r '.properties.outputs.webAppUrl.value')

echo "✅ Deployment completed successfully!"
echo "📱 App Name: $WEB_APP_NAME"
echo "🌐 URL: $WEB_APP_URL"

# Deploy application code
echo "📦 Deploying application code..."
zip -r pharmassist-deploy.zip pharmassist_app.py pdf_processing.py requirements.txt templates/

az webapp deployment source config-zip \
    --resource-group "$RESOURCE_GROUP" \
    --name "$WEB_APP_NAME" \
    --src pharmassist-deploy.zip

# Configure startup command
echo "⚙️ Configuring startup command..."
az webapp config set \
    --resource-group "$RESOURCE_GROUP" \
    --name "$WEB_APP_NAME" \
    --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 pharmassist_app:app"

# Restart app
echo "🔄 Restarting application..."
az webapp restart \
    --resource-group "$RESOURCE_GROUP" \
    --name "$WEB_APP_NAME"

echo ""
echo "🎉 PharmAssist deployment complete!"
echo "🌐 Access your application at: $WEB_APP_URL"
echo "🔍 Health check: $WEB_APP_URL/health"
echo "📊 API status: $WEB_APP_URL/api/status"
