# PowerShell Azure deployment for pharmacy PDF processor

# Configuration
$RESOURCE_GROUP = "pharmchat-rg"
$LOCATION = "East US"
$APP_NAME = "pharmacy-pdf-processor-km"
$PLAN_NAME = "pharmacy-plan-free"

Write-Host "🏥 Creating Azure deployment for Pharmacy PDF Processor..." -ForegroundColor Green

# Create resource group
Write-Host "Creating resource group: $RESOURCE_GROUP" -ForegroundColor Cyan
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create app service plan  
Write-Host "Creating app service plan: $PLAN_NAME" -ForegroundColor Cyan
az appservice plan create --name $PLAN_NAME --resource-group $RESOURCE_GROUP --sku F1 --is-linux

# Create web app
Write-Host "Creating web app: $APP_NAME" -ForegroundColor Cyan  
az webapp create --resource-group $RESOURCE_GROUP --plan $PLAN_NAME --name $APP_NAME --runtime "PYTHON|3.11"

# Configure startup command
Write-Host "Configuring startup command..." -ForegroundColor Cyan
az webapp config set --name $APP_NAME --resource-group $RESOURCE_GROUP --startup-file "python simple_app.py"

Write-Host "✅ Deployment infrastructure complete!" -ForegroundColor Green
Write-Host "🌐 Your pharmacy app will be available at: https://$APP_NAME.azurewebsites.net" -ForegroundColor Yellow
