# PharmAssist Enterprise Deployment Script
# Based on Microsoft.Web-WebAppDatabase-Portal template

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "Central US",
    
    [Parameter(Mandatory=$false)]
    [string]$WebAppName = "pharmassist-enterprise",
    
    [Parameter(Mandatory=$false)]
    [string]$DatabasePassword = "PharmAssist2025!",
    
    [Parameter(Mandatory=$false)]
    [string]$SubscriptionId
)

Write-Host "🏥 PharmAssist Enterprise Deployment" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Set subscription if provided
if ($SubscriptionId) {
    Write-Host "Setting subscription to: $SubscriptionId" -ForegroundColor Yellow
    az account set --subscription $SubscriptionId
}

# Check if logged in to Azure
$account = az account show --query "name" -o tsv 2>$null
if (!$account) {
    Write-Host "❌ Not logged in to Azure. Please run 'az login' first." -ForegroundColor Red
    exit 1
}

Write-Host "✓ Logged in to Azure as: $account" -ForegroundColor Green

# Create resource group
Write-Host "Creating resource group: $ResourceGroupName in $Location" -ForegroundColor Yellow
az group create --name $ResourceGroupName --location $Location

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create resource group" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Resource group created successfully" -ForegroundColor Green

# Deploy ARM template
Write-Host "Deploying PharmAssist Enterprise infrastructure..." -ForegroundColor Yellow

$deploymentName = "pharmassist-enterprise-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

# Update parameters with user values
$parameters = @{
    "webAppName" = @{ "value" = $WebAppName }
    "location" = @{ "value" = $Location }
    "administratorLoginPassword" = @{ "value" = $DatabasePassword }
}

$parametersJson = $parameters | ConvertTo-Json -Depth 3

# Save temporary parameters file
$tempParamsFile = "temp-params-$(Get-Date -Format 'yyyyMMddHHmmss').json"
$parametersJson | Out-File -FilePath $tempParamsFile -Encoding UTF8

try {
    $deployment = az deployment group create `
        --resource-group $ResourceGroupName `
        --template-file "pharmassist-enterprise-template.json" `
        --parameters "@$tempParamsFile" `
        --name $deploymentName `
        --query "properties.outputs" -o json

    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ ARM template deployment failed" -ForegroundColor Red
        exit 1
    }

    $outputs = $deployment | ConvertFrom-Json
    $webAppUrl = $outputs.webAppUrl.value
    $databaseServer = $outputs.databaseServer.value

    Write-Host "✓ Infrastructure deployed successfully" -ForegroundColor Green
    Write-Host "Web App URL: $webAppUrl" -ForegroundColor Cyan
    Write-Host "Database Server: $databaseServer" -ForegroundColor Cyan

} finally {
    # Clean up temporary file
    if (Test-Path $tempParamsFile) {
        Remove-Item $tempParamsFile
    }
}

# Deploy application code
Write-Host "Deploying PharmAssist application code..." -ForegroundColor Yellow

# Create deployment package
$deploymentPackage = "pharmassist-enterprise-deploy.zip"

if (Test-Path $deploymentPackage) {
    Remove-Item $deploymentPackage
}

# Create zip with enterprise files
$filesToInclude = @(
    "pharmassist_enterprise.py",
    "pdf_processing.py",
    "requirements_enterprise.txt",
    "templates/",
    "static/"
)

# Check if files exist
$missingFiles = @()
foreach ($file in $filesToInclude) {
    if (!(Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "❌ Missing required files:" -ForegroundColor Red
    $missingFiles | ForEach-Object { Write-Host "   - $_" -ForegroundColor Red }
    Write-Host "Please ensure all PharmAssist files are present." -ForegroundColor Red
    exit 1
}

# Create deployment ZIP
Add-Type -AssemblyName System.IO.Compression.FileSystem

$zipFile = [System.IO.Compression.ZipFile]::Open($deploymentPackage, [System.IO.Compression.ZipArchiveMode]::Create)

try {
    # Add main application file
    $entry = $zipFile.CreateEntry("app.py")
    $entryStream = $entry.Open()
    $fileStream = [System.IO.File]::OpenRead("pharmassist_enterprise.py")
    $fileStream.CopyTo($entryStream)
    $fileStream.Close()
    $entryStream.Close()

    # Add requirements file
    $entry = $zipFile.CreateEntry("requirements.txt")
    $entryStream = $entry.Open()
    $fileStream = [System.IO.File]::OpenRead("requirements_enterprise.txt")
    $fileStream.CopyTo($entryStream)
    $fileStream.Close()
    $entryStream.Close()

    # Add PDF processing if available
    if (Test-Path "pdf_processing.py") {
        $entry = $zipFile.CreateEntry("pdf_processing.py")
        $entryStream = $entry.Open()
        $fileStream = [System.IO.File]::OpenRead("pdf_processing.py")
        $fileStream.CopyTo($entryStream)
        $fileStream.Close()
        $entryStream.Close()
    }

    # Add templates directory
    if (Test-Path "templates") {
        Get-ChildItem "templates" -Recurse -File | ForEach-Object {
            $relativePath = $_.FullName.Substring((Get-Location).Path.Length + 1)
            $entry = $zipFile.CreateEntry($relativePath.Replace('\', '/'))
            $entryStream = $entry.Open()
            $fileStream = [System.IO.File]::OpenRead($_.FullName)
            $fileStream.CopyTo($entryStream)
            $fileStream.Close()
            $entryStream.Close()
        }
    }

    # Add static directory if it exists
    if (Test-Path "static") {
        Get-ChildItem "static" -Recurse -File | ForEach-Object {
            $relativePath = $_.FullName.Substring((Get-Location).Path.Length + 1)
            $entry = $zipFile.CreateEntry($relativePath.Replace('\', '/'))
            $entryStream = $entry.Open()
            $fileStream = [System.IO.File]::OpenRead($_.FullName)
            $fileStream.CopyTo($entryStream)
            $fileStream.Close()
            $entryStream.Close()
        }
    }

} finally {
    $zipFile.Dispose()
}

Write-Host "✓ Deployment package created: $deploymentPackage" -ForegroundColor Green

# Deploy to Azure App Service
Write-Host "Uploading application to Azure..." -ForegroundColor Yellow

az webapp deployment source config-zip `
    --resource-group $ResourceGroupName `
    --name $WebAppName `
    --src $deploymentPackage

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Application deployment failed" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Application deployed successfully" -ForegroundColor Green

# Configure app settings for database
Write-Host "Configuring database connection..." -ForegroundColor Yellow

az webapp config appsettings set `
    --resource-group $ResourceGroupName `
    --name $WebAppName `
    --settings WEBSITES_ENABLE_APP_SERVICE_STORAGE=false

Write-Host "✓ Application configuration updated" -ForegroundColor Green

# Final output
Write-Host "" -ForegroundColor Green
Write-Host "🎉 PharmAssist Enterprise Deployment Complete!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host "Web App URL: $webAppUrl" -ForegroundColor Cyan
Write-Host "Database Server: $databaseServer" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Green
Write-Host "Features enabled:" -ForegroundColor White
Write-Host "  ✓ PDF document processing" -ForegroundColor Green
Write-Host "  ✓ PostgreSQL database with processing history" -ForegroundColor Green
Write-Host "  ✓ Session tracking and analytics" -ForegroundColor Green
Write-Host "  ✓ CareTend format conversion" -ForegroundColor Green
Write-Host "  ✓ Enterprise-grade security" -ForegroundColor Green
Write-Host "" -ForegroundColor Green
Write-Host "Database credentials:" -ForegroundColor White
Write-Host "  Username: pharmadmin" -ForegroundColor Yellow
Write-Host "  Password: $DatabasePassword" -ForegroundColor Yellow
Write-Host "" -ForegroundColor Green
Write-Host "The application should be available in 2-3 minutes." -ForegroundColor White

# Clean up
Remove-Item $deploymentPackage -ErrorAction SilentlyContinue
