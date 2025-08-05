@echo off
setlocal enabledelayedexpansion

REM Azure Deployment Script for PharmAssist Enterprise PDF Extraction Tool (Windows)
REM This script automates the deployment to Azure App Service for PDF extraction only

echo 🚀 Starting Azure deployment for PharmAssist Enterprise PDF Extraction Tool...

REM Configuration
set RESOURCE_GROUP=pharmassist-rg
set LOCATION=East US
set APP_NAME=pharmassist-pdf-extract
set PLAN_NAME=pharmassist-plan
set DB_SERVER_NAME=pharmassist-db-server
set DB_ADMIN_USER=dbadmin
set DB_NAME=pharmassist_pdf
set INSIGHTS_NAME=pharmassist-insights

REM Check if Azure CLI is installed
where az >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Azure CLI is not installed. Please install it first:
    echo https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows
    pause
    exit /b 1
)

REM Check if user is logged in to Azure
az account show >nul 2>nul
if %errorlevel% neq 0 (
    echo WARNING: You are not logged in to Azure. Please login first.
    az login
)

REM Get current subscription
for /f "tokens=*" %%i in ('az account show --query "name" -o tsv') do set SUBSCRIPTION=%%i
echo INFO: Using subscription: !SUBSCRIPTION!

REM Ask for confirmation
set /p REPLY="Do you want to continue with the deployment? (y/N): "
if /i not "!REPLY!"=="y" (
    echo WARNING: Deployment cancelled.
    pause
    exit /b 0
)

REM Generate secure passwords
echo INFO: Generating secure passwords...
for /f "tokens=*" %%i in ('python -c "import secrets; print(secrets.token_urlsafe(32))"') do set SECRET_KEY=%%i
for /f "tokens=*" %%i in ('python -c "import secrets; print(secrets.token_urlsafe(24))"') do set DB_PASSWORD=%%i

echo SUCCESS: Generated secure passwords

REM Create resource group
echo INFO: Creating resource group: %RESOURCE_GROUP%
az group create --name %RESOURCE_GROUP% --location "%LOCATION%" --output none
if %errorlevel% neq 0 (
    echo ERROR: Failed to create resource group
    pause
    exit /b 1
)
echo SUCCESS: Resource group created

REM Create PostgreSQL server
echo INFO: Creating PostgreSQL server: %DB_SERVER_NAME%
az postgres flexible-server create --resource-group %RESOURCE_GROUP% --name %DB_SERVER_NAME% --location "%LOCATION%" --admin-user %DB_ADMIN_USER% --admin-password "!DB_PASSWORD!" --sku-name Standard_B1ms --tier Burstable --version 15 --storage-size 32 --output none
if %errorlevel% neq 0 (
    echo ERROR: Failed to create PostgreSQL server
    pause
    exit /b 1
)
echo SUCCESS: PostgreSQL server created

REM Create database
echo INFO: Creating database: %DB_NAME%
az postgres flexible-server db create --resource-group %RESOURCE_GROUP% --server-name %DB_SERVER_NAME% --database-name %DB_NAME% --output none
if %errorlevel% neq 0 (
    echo ERROR: Failed to create database
    pause
    exit /b 1
)
echo SUCCESS: Database created

REM Configure firewall for Azure services
echo INFO: Configuring database firewall rules
az postgres flexible-server firewall-rule create --resource-group %RESOURCE_GROUP% --name %DB_SERVER_NAME% --rule-name AllowAzureServices --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0 --output none
if %errorlevel% neq 0 (
    echo ERROR: Failed to configure database firewall
    pause
    exit /b 1
)
echo SUCCESS: Database firewall configured

REM Skipping Redis cache creation (not needed for PDF extraction)

REM Create App Service plan
echo INFO: Creating App Service plan: %PLAN_NAME%
az appservice plan create --resource-group %RESOURCE_GROUP% --name %PLAN_NAME% --location "%LOCATION%" --sku B1 --is-linux --output none
if %errorlevel% neq 0 (
    echo ERROR: Failed to create App Service plan
    pause
    exit /b 1
)
echo SUCCESS: App Service plan created

REM Create Web App
echo INFO: Creating Web App: %APP_NAME%
az webapp create --resource-group %RESOURCE_GROUP% --plan %PLAN_NAME% --name %APP_NAME% --runtime "PYTHON:3.11" --output none
if %errorlevel% neq 0 (
    echo ERROR: Failed to create Web App
    pause
    exit /b 1
)
echo SUCCESS: Web App created

REM Create Application Insights
echo INFO: Creating Application Insights: %INSIGHTS_NAME%
az monitor app-insights component create --resource-group %RESOURCE_GROUP% --app %INSIGHTS_NAME% --location "%LOCATION%" --application-type web --output none
if %errorlevel% neq 0 (
    echo ERROR: Failed to create Application Insights
    pause
    exit /b 1
)
echo SUCCESS: Application Insights created

REM Get connection strings and keys
for /f "tokens=*" %%i in ('az postgres flexible-server show --resource-group %RESOURCE_GROUP% --name %DB_SERVER_NAME% --query "fullyQualifiedDomainName" -o tsv') do set DB_HOST=%%i
for /f "tokens=*" %%i in ('az monitor app-insights component show --resource-group %RESOURCE_GROUP% --app %INSIGHTS_NAME% --query "instrumentationKey" -o tsv') do set INSIGHTS_KEY=%%i

echo SUCCESS: Retrieved connection details

REM Configure app settings
echo INFO: Configuring application settings...

set DATABASE_URL=postgresql://%DB_ADMIN_USER%:!DB_PASSWORD!@!DB_HOST!:5432/%DB_NAME%?sslmode=require

az webapp config appsettings set --resource-group %RESOURCE_GROUP% --name %APP_NAME% --settings FLASK_ENV=production SECRET_KEY="!SECRET_KEY!" DATABASE_URL="!DATABASE_URL!" APPINSIGHTS_INSTRUMENTATIONKEY="!INSIGHTS_KEY!" WEBSITES_PORT=5000 SCM_DO_BUILD_DURING_DEPLOYMENT=true WTF_CSRF_ENABLED=True SESSION_COOKIE_SECURE=True SESSION_COOKIE_HTTPONLY=True FORCE_HTTPS=True --output none

if %errorlevel% neq 0 (
    echo ERROR: Failed to configure application settings
    pause
    exit /b 1
)
echo SUCCESS: Application settings configured

REM Configure startup command
echo INFO: Configuring startup command...
az webapp config set --resource-group %RESOURCE_GROUP% --name %APP_NAME% --startup-file "gunicorn --bind 0.0.0.0:5000 app:app" --output none
if %errorlevel% neq 0 (
    echo ERROR: Failed to configure startup command
    pause
    exit /b 1
)
echo SUCCESS: Startup command configured

REM Configure health check
echo INFO: Configuring health check...
az webapp config set --resource-group %RESOURCE_GROUP% --name %APP_NAME% --health-check-path "/api/health" --output none
if %errorlevel% neq 0 (
    echo ERROR: Failed to configure health check
    pause
    exit /b 1
)
echo SUCCESS: Health check configured

REM Set up local Git deployment
echo INFO: Setting up Git deployment...
for /f "tokens=*" %%i in ('az webapp deployment source config-local-git --resource-group %RESOURCE_GROUP% --name %APP_NAME% --query "url" -o tsv') do set DEPLOY_URL=%%i

echo SUCCESS: Git deployment configured

REM Create environment file
echo INFO: Creating local environment file...
(
echo # Azure Environment Configuration
echo FLASK_ENV=production
echo SECRET_KEY=!SECRET_KEY!
echo DATABASE_URL=!DATABASE_URL!
echo APPINSIGHTS_INSTRUMENTATIONKEY=!INSIGHTS_KEY!
echo.
echo # Database Admin Credentials ^(for backup purposes^)
echo DB_ADMIN_USER=%DB_ADMIN_USER%
echo DB_ADMIN_PASSWORD=!DB_PASSWORD!
echo DB_HOST=!DB_HOST!
echo DB_NAME=%DB_NAME%
echo.
echo # Azure Resource Details
echo RESOURCE_GROUP=%RESOURCE_GROUP%
echo APP_NAME=%APP_NAME%
) > .env.azure

echo SUCCESS: Environment file created: .env.azure

REM Add Azure remote if it doesn't exist
git remote get-url azure >nul 2>nul
if %errorlevel% neq 0 (
    echo INFO: Adding Azure Git remote...
    git remote add azure "!DEPLOY_URL!"
    echo SUCCESS: Azure remote added
) else (
    echo WARNING: Azure remote already exists
)

REM Deploy to Azure
echo INFO: Deploying application to Azure...
echo This may take several minutes...

git push azure main
if %errorlevel% neq 0 (
    echo ERROR: Deployment failed. Check the output above for errors.
    pause
    exit /b 1
)

echo SUCCESS: Application deployed successfully!

REM Get the app URL
set APP_URL=https://%APP_NAME%.azurewebsites.net

REM Wait for deployment to complete
echo INFO: Waiting for application to start...
timeout /t 30 /nobreak >nul

REM Display deployment summary
echo.
echo 🎉 Deployment completed successfully!
echo.
echo 📋 Deployment Summary:
echo ====================
echo Resource Group: %RESOURCE_GROUP%
echo App Service: %APP_NAME%
echo Database Server: %DB_SERVER_NAME%
echo Application URL: !APP_URL!
echo Health Check: !APP_URL!/api/health
echo.
echo 📁 Configuration files created:
echo - .env.azure ^(contains all connection details^)
echo.
echo 🔑 Important Security Notes:
echo - Database password: !DB_PASSWORD! ^(saved in .env.azure^)
echo - Secret key generated and configured
echo - HTTPS is enforced
echo.
echo 📊 Monitoring:
echo - Application Insights: Access via Azure Portal
echo - App Service logs: az webapp log tail --resource-group %RESOURCE_GROUP% --name %APP_NAME%
echo.
echo 🛠 Next Steps:
echo 1. Configure your custom domain and SSL certificate
echo 2. Set up your email provider ^(SendGrid^) API key
echo 3. Configure OAuth providers if needed
echo 4. Set up monitoring alerts
echo 5. Test all functionality
echo.
echo SUCCESS: Azure deployment script completed!

pause