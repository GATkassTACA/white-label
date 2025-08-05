# InktelliAssist Pro Deployment Script
# Professional AI Document Processing for Tattoo Parlors
# Based on proven PharmAssist architecture

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName = "InktelliAssist-RG",
    
    [Parameter(Mandatory=$true)]
    [string]$Location = "East US",
    
    [Parameter(Mandatory=$false)]
    [string]$AppServiceName = "inktelliassist-pro",
    
    [Parameter(Mandatory=$false)]
    [string]$DatabaseServerName = "inktelliassist-server-$(Get-Random -Minimum 1000 -Maximum 9999)",
    
    [Parameter(Mandatory=$false)]
    [string]$DatabaseName = "inktelliassist-db"
)

Write-Host "🎨 INKTELLIASSIST PRO DEPLOYMENT" -ForegroundColor Magenta
Write-Host "Professional Intelligence for Ink Artists" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Magenta
Write-Host ""

# Check if Azure CLI is installed
try {
    az version | Out-Null
    Write-Host "✅ Azure CLI detected" -ForegroundColor Green
} catch {
    Write-Host "❌ Azure CLI not found. Please install Azure CLI first." -ForegroundColor Red
    exit 1
}

# Login to Azure
Write-Host "🔐 Logging into Azure..." -ForegroundColor Yellow
az login

# Set subscription (optional - will use default)
$subscription = az account show --query "name" -o tsv
Write-Host "📋 Using subscription: $subscription" -ForegroundColor Cyan

# Create Resource Group
Write-Host "📦 Creating Resource Group: $ResourceGroupName" -ForegroundColor Yellow
az group create --name $ResourceGroupName --location $Location

# Create App Service Plan
Write-Host "🚀 Creating App Service Plan..." -ForegroundColor Yellow
az appservice plan create `
    --name "$AppServiceName-plan" `
    --resource-group $ResourceGroupName `
    --location $Location `
    --sku B1 `
    --is-linux

# Create PostgreSQL Server
Write-Host "🗄️ Creating PostgreSQL Server: $DatabaseServerName" -ForegroundColor Yellow
$adminUser = "inktelliassist_admin"
$adminPassword = -join ((33..126) | Get-Random -Count 16 | ForEach-Object {[char]$_})

az postgres flexible-server create `
    --name $DatabaseServerName `
    --resource-group $ResourceGroupName `
    --location $Location `
    --admin-user $adminUser `
    --admin-password $adminPassword `
    --sku-name Standard_B1ms `
    --tier Burstable `
    --storage-size 32 `
    --version 13

# Create Database
Write-Host "📊 Creating Database: $DatabaseName" -ForegroundColor Yellow
az postgres flexible-server db create `
    --resource-group $ResourceGroupName `
    --server-name $DatabaseServerName `
    --database-name $DatabaseName

# Configure Firewall (allow Azure services)
Write-Host "🔥 Configuring Firewall..." -ForegroundColor Yellow
az postgres flexible-server firewall-rule create `
    --resource-group $ResourceGroupName `
    --name $DatabaseServerName `
    --rule-name "AllowAzureServices" `
    --start-ip-address 0.0.0.0 `
    --end-ip-address 0.0.0.0

# Create Web App
Write-Host "🌐 Creating Web App: $AppServiceName" -ForegroundColor Yellow
az webapp create `
    --name $AppServiceName `
    --resource-group $ResourceGroupName `
    --plan "$AppServiceName-plan" `
    --runtime "PYTHON|3.9"

# Get database connection details
$serverFQDN = az postgres flexible-server show `
    --resource-group $ResourceGroupName `
    --name $DatabaseServerName `
    --query "fullyQualifiedDomainName" -o tsv

# Configure App Settings
Write-Host "⚙️ Configuring Application Settings..." -ForegroundColor Yellow
az webapp config appsettings set `
    --resource-group $ResourceGroupName `
    --name $AppServiceName `
    --settings `
        "DATABASE_HOST=$serverFQDN" `
        "DATABASE_NAME=$DatabaseName" `
        "DATABASE_USER=$adminUser" `
        "DATABASE_PASSWORD=$adminPassword" `
        "FLASK_ENV=production" `
        "APP_NAME=InktelliAssist Pro" `
        "BRAND_COLOR=#000000" `
        "ACCENT_COLOR=#DC143C" `
        "HIGHLIGHT_COLOR=#00BFFF" `
        "SCM_DO_BUILD_DURING_DEPLOYMENT=true"

Write-Host ""
Write-Host "🎯 DEPLOYMENT SUMMARY" -ForegroundColor Magenta
Write-Host "===================" -ForegroundColor Magenta
Write-Host "Resource Group: $ResourceGroupName" -ForegroundColor White
Write-Host "App Service: $AppServiceName" -ForegroundColor White
Write-Host "Database Server: $DatabaseServerName" -ForegroundColor White
Write-Host "Database: $DatabaseName" -ForegroundColor White
Write-Host "Admin User: $adminUser" -ForegroundColor White
Write-Host "Admin Password: $adminPassword" -ForegroundColor Yellow
Write-Host ""
Write-Host "🌐 Application URL: https://$AppServiceName.azurewebsites.net" -ForegroundColor Green
Write-Host ""
Write-Host "📝 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Deploy the application code using Git or ZIP deployment" -ForegroundColor White
Write-Host "2. Test the application at the URL above" -ForegroundColor White
Write-Host "3. Create admin user account" -ForegroundColor White
Write-Host "4. Configure custom domain (optional)" -ForegroundColor White
Write-Host ""

# Save credentials to file
$credentialsFile = "inktelliassist-credentials.txt"
@"
InktelliAssist Pro Deployment Credentials
=========================================
Date: $(Get-Date)
Resource Group: $ResourceGroupName
App Service: $AppServiceName
Database Server: $DatabaseServerName
Database Name: $DatabaseName
Admin User: $adminUser
Admin Password: $adminPassword
Connection String: postgresql://$adminUser`:$adminPassword@$serverFQDN/$DatabaseName
Application URL: https://$AppServiceName.azurewebsites.net

SAVE THIS FILE SECURELY!
"@ | Out-File -FilePath $credentialsFile -Encoding UTF8

Write-Host "💾 Credentials saved to: $credentialsFile" -ForegroundColor Green
Write-Host "⚠️  IMPORTANT: Save this file securely and delete from this location!" -ForegroundColor Red
