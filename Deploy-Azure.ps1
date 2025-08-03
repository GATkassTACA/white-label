# Azure Infrastructure Deployment Script (PowerShell)
# This script deploys the white-label chat platform using ARM templates

param(
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroupName = "white-label-rg",
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "East US",
    
    [Parameter(Mandatory=$false)]
    [string]$AppName = "white-label-chat",
    
    [Parameter(Mandatory=$false)]
    [string]$Environment = "prod",
    
    [Parameter(Mandatory=$false)]
    [string]$SubscriptionId,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipConfirmation
)

# Function to write colored output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✅ $Message" -Color "Green"
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "ℹ️  $Message" -Color "Cyan"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠️  $Message" -Color "Yellow"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "❌ $Message" -Color "Red"
}

# Check if Azure PowerShell module is installed
Write-Info "Checking Azure PowerShell module..."
if (-not (Get-Module -ListAvailable -Name Az)) {
    Write-Warning "Azure PowerShell module is not installed."
    $installChoice = Read-Host "Would you like to install it? (y/N)"
    if ($installChoice -eq 'y' -or $installChoice -eq 'Y') {
        Write-Info "Installing Azure PowerShell module..."
        Install-Module -Name Az -Repository PSGallery -Force -AllowClobber
        Write-Success "Azure PowerShell module installed successfully"
    } else {
        Write-Error "Azure PowerShell module is required. Exiting..."
        exit 1
    }
}

# Import Azure module
Import-Module Az

# Check if user is logged in
Write-Info "Checking Azure login status..."
$context = Get-AzContext
if (-not $context) {
    Write-Warning "You are not logged in to Azure."
    Write-Info "Initiating Azure login..."
    Connect-AzAccount
    $context = Get-AzContext
}

Write-Success "Logged in as: $($context.Account.Id)"

# Set subscription if provided
if ($SubscriptionId) {
    Write-Info "Setting subscription to: $SubscriptionId"
    Set-AzContext -SubscriptionId $SubscriptionId
}

$currentSubscription = (Get-AzContext).Subscription
Write-Info "Using subscription: $($currentSubscription.Name) ($($currentSubscription.Id))"

# Confirm deployment parameters
Write-Host ""
Write-Host "🚀 Azure Deployment Configuration" -ForegroundColor Magenta
Write-Host "=================================" -ForegroundColor Magenta
Write-Host "Resource Group: $ResourceGroupName"
Write-Host "Location: $Location"
Write-Host "App Name: $AppName"
Write-Host "Environment: $Environment"
Write-Host "Subscription: $($currentSubscription.Name)"
Write-Host ""

if (-not $SkipConfirmation) {
    $confirm = Read-Host "Do you want to proceed with the deployment? (y/N)"
    if ($confirm -ne 'y' -and $confirm -ne 'Y') {
        Write-Warning "Deployment cancelled."
        exit 0
    }
}

# Generate secure password for database
Write-Info "Generating secure database password..."
$DatabasePassword = -join ((33..126) | Get-Random -Count 32 | ForEach-Object {[char]$_})
Write-Success "Secure password generated"

# Create resource group if it doesn't exist
Write-Info "Creating resource group: $ResourceGroupName"
$rg = Get-AzResourceGroup -Name $ResourceGroupName -ErrorAction SilentlyContinue
if (-not $rg) {
    New-AzResourceGroup -Name $ResourceGroupName -Location $Location
    Write-Success "Resource group created successfully"
} else {
    Write-Warning "Resource group already exists"
}

# Prepare deployment parameters
$deploymentParams = @{
    appName = $AppName
    environment = $Environment
    location = $Location
    databaseAdminPassword = (ConvertTo-SecureString $DatabasePassword -AsPlainText -Force)
    appServicePlanSku = "B1"
    postgresqlSku = "Standard_B1ms"
    redisSku = "Basic"
    redisCapacity = 0
}

# Deploy ARM template
Write-Info "Starting ARM template deployment..."
Write-Info "This may take 10-15 minutes..."

$deploymentName = "white-label-deployment-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

try {
    $deployment = New-AzResourceGroupDeployment `
        -ResourceGroupName $ResourceGroupName `
        -Name $deploymentName `
        -TemplateFile "azure-infrastructure.json" `
        -TemplateParameterObject $deploymentParams `
        -Verbose

    if ($deployment.ProvisioningState -eq "Succeeded") {
        Write-Success "ARM template deployment completed successfully!"
    } else {
        Write-Error "ARM template deployment failed with state: $($deployment.ProvisioningState)"
        exit 1
    }
} catch {
    Write-Error "ARM template deployment failed: $($_.Exception.Message)"
    exit 1
}

# Extract outputs from deployment
$outputs = $deployment.Outputs
$webAppName = $outputs.webAppName.Value
$webAppUrl = $outputs.webAppUrl.Value
$postgresqlFQDN = $outputs.postgresqlFQDN.Value
$redisHostName = $outputs.redisHostName.Value
$appInsightsKey = $outputs.appInsightsInstrumentationKey.Value
$storageAccountName = $outputs.storageAccountName.Value

Write-Success "Infrastructure deployment completed!"

# Generate environment configuration file
Write-Info "Creating environment configuration file..."

$envConfig = @"
# Azure Environment Configuration - Generated $(Get-Date)
FLASK_ENV=production
SECRET_KEY=$(([System.Web.Security.Membership]::GeneratePassword(32, 8)))
DATABASE_URL=postgresql://dbadmin:$DatabasePassword@$($postgresqlFQDN):5432/whitelabel_chat?sslmode=require
REDIS_URL=redis://default:REDIS_KEY_PLACEHOLDER@$($redisHostName):6380/0?ssl_cert_reqs=required
APPINSIGHTS_INSTRUMENTATIONKEY=$appInsightsKey

# Database Configuration
DB_ADMIN_USER=dbadmin
DB_ADMIN_PASSWORD=$DatabasePassword
DB_HOST=$postgresqlFQDN
DB_NAME=whitelabel_chat

# Azure Resource Names
RESOURCE_GROUP=$ResourceGroupName
WEB_APP_NAME=$webAppName
STORAGE_ACCOUNT_NAME=$storageAccountName

# Security Settings
WTF_CSRF_ENABLED=True
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
FORCE_HTTPS=True

# Email Configuration (Replace with your SendGrid API key)
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key-here
MAIL_DEFAULT_SENDER=noreply@yourdomain.com
"@

# Get Redis access key and update the environment file
Write-Info "Retrieving Redis access key..."
$redisKeys = Get-AzRedisCacheKey -ResourceGroupName $ResourceGroupName -Name $outputs.redisName.Value
$redisKey = $redisKeys.PrimaryKey
$envConfig = $envConfig.Replace("REDIS_KEY_PLACEHOLDER", $redisKey)

# Save environment configuration
$envConfig | Out-File -FilePath ".env.azure" -Encoding UTF8
Write-Success "Environment configuration saved to .env.azure"

# Set up Git deployment if Git repository exists
if (Test-Path ".git") {
    Write-Info "Setting up Git deployment..."
    
    # Get publishing credentials
    $publishingCredentials = Invoke-AzResourceAction `
        -ResourceGroupName $ResourceGroupName `
        -ResourceType "Microsoft.Web/sites/config" `
        -ResourceName "$webAppName/publishingsource" `
        -Action "list" `
        -ApiVersion "2021-02-01" `
        -Force
    
    $gitUrl = "https://$($publishingCredentials.properties.repoUrl)"
    
    # Add Azure remote if it doesn't exist
    $gitRemotes = git remote
    if ($gitRemotes -notcontains "azure") {
        git remote add azure $gitUrl
        Write-Success "Azure Git remote added"
    } else {
        Write-Warning "Azure Git remote already exists"
    }
    
    # Configure local Git for deployment
    Write-Info "Configuring Git deployment..."
    $deploymentConfig = @{
        repoUrl = $gitUrl
        branch = "main"
        isManualIntegration = $true
    }
    
    # Enable local Git deployment
    Set-AzWebApp -ResourceGroupName $ResourceGroupName -Name $webAppName -AppSettings @{
        "SCM_DO_BUILD_DURING_DEPLOYMENT" = "true"
        "ENABLE_ORYX_BUILD" = "true"
    }
    
    Write-Success "Git deployment configured"
    Write-Info "Deploy with: git push azure main"
}

# Display deployment summary
Write-Host ""
Write-Host "🎉 Deployment Summary" -ForegroundColor Green
Write-Host "=====================" -ForegroundColor Green
Write-Host "Resource Group: $ResourceGroupName"
Write-Host "Web App: $webAppName"
Write-Host "Application URL: $webAppUrl"
Write-Host "Health Check: $webAppUrl/api/health"
Write-Host "Database Server: $($outputs.postgresqlServerName.Value)"
Write-Host "Redis Cache: $($outputs.redisName.Value)"
Write-Host "Storage Account: $storageAccountName"
Write-Host "Application Insights: $($outputs.appInsightsName.Value)"
Write-Host ""

Write-Host "📁 Files Created:" -ForegroundColor Cyan
Write-Host "- .env.azure (environment configuration)"
Write-Host ""

Write-Host "🔐 Security Information:" -ForegroundColor Yellow
Write-Host "- Database password: $DatabasePassword"
Write-Host "- All passwords saved in .env.azure"
Write-Host "- HTTPS enforced on all services"
Write-Host "- Redis SSL/TLS enabled"
Write-Host ""

Write-Host "📊 Monitoring:" -ForegroundColor Magenta
Write-Host "- Application Insights: https://portal.azure.com/#resource/subscriptions/$($currentSubscription.Id)/resourceGroups/$ResourceGroupName/providers/Microsoft.Insights/components/$($outputs.appInsightsName.Value)"
Write-Host "- Azure Portal: https://portal.azure.com/#resource/subscriptions/$($currentSubscription.Id)/resourceGroups/$ResourceGroupName"
Write-Host ""

Write-Host "🚀 Next Steps:" -ForegroundColor Blue
Write-Host "1. Deploy your application: git push azure main"
Write-Host "2. Configure SendGrid API key in Azure App Settings"
Write-Host "3. Set up custom domain and SSL certificate"
Write-Host "4. Configure monitoring alerts"
Write-Host "5. Test the application: $webAppUrl"
Write-Host ""

Write-Success "Azure deployment completed successfully!"

# Optionally open Azure portal
$openPortal = Read-Host "Would you like to open the Azure Portal? (y/N)"
if ($openPortal -eq 'y' -or $openPortal -eq 'Y') {
    $portalUrl = "https://portal.azure.com/#resource/subscriptions/$($currentSubscription.Id)/resourceGroups/$ResourceGroupName"
    Start-Process $portalUrl
}
