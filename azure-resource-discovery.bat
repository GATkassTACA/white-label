@echo off
setlocal enabledelayedexpansion

echo 🔍 Azure Resource Discovery Helper
echo ===================================
echo This script helps you find the connection strings and keys you need
echo for configuring your white-label chat application.
echo.

set /p RESOURCE_GROUP="Enter your Resource Group name (default: white-label-rg): "
if "!RESOURCE_GROUP!"=="" set RESOURCE_GROUP=white-label-rg

echo.
echo ℹ️  Discovering resources in: !RESOURCE_GROUP!
echo.

REM Note: This script provides the commands to run rather than executing them
REM because Azure CLI may not be configured in the current session

echo 📋 AZURE CLI COMMANDS TO GET YOUR CONNECTION DETAILS:
echo =====================================================
echo.
echo 1. LIST ALL RESOURCES:
echo    az resource list --resource-group !RESOURCE_GROUP! --output table
echo.
echo 2. GET DATABASE CONNECTION STRING:
echo    az postgres flexible-server show --resource-group !RESOURCE_GROUP! --name [YOUR_DB_SERVER_NAME] --query "fullyQualifiedDomainName"
echo.
echo 3. GET REDIS CONNECTION DETAILS:
echo    az redis show --resource-group !RESOURCE_GROUP! --name [YOUR_REDIS_NAME] --query "{hostname:hostName,port:port}"
echo    az redis list-keys --resource-group !RESOURCE_GROUP! --name [YOUR_REDIS_NAME] --query "primaryKey"
echo.
echo 4. GET APP SERVICE DETAILS:
echo    az webapp show --resource-group !RESOURCE_GROUP! --name [YOUR_APP_NAME] --query "{url:defaultHostName,state:state}"
echo.
echo 5. GET APPLICATION INSIGHTS KEY:
echo    az monitor app-insights component show --resource-group !RESOURCE_GROUP! --app [YOUR_INSIGHTS_NAME] --query "instrumentationKey"
echo.

echo 🌐 ALTERNATIVE: Use Azure Portal (Easier):
echo ==========================================
echo 1. Go to https://portal.azure.com
echo 2. Navigate to Resource Groups ^> !RESOURCE_GROUP!
echo 3. Click on each resource to get connection details:
echo.
echo    📊 App Service:
echo    - Get the URL from Overview page
echo    - Configure environment variables in Configuration ^> Application Settings
echo.
echo    🗄️  PostgreSQL Database:
echo    - Go to Connection strings
echo    - Copy the connection string
echo    - Replace {your_password} with your actual password
echo.
echo    🔄 Redis Cache:
echo    - Go to Access keys
echo    - Copy Primary connection string
echo    - Or copy Primary key and hostname separately
echo.
echo    📈 Application Insights:
echo    - Go to Overview
echo    - Copy Instrumentation Key
echo.

echo 📝 QUICK SETUP CHECKLIST:
echo =========================
echo □ Found your App Service URL
echo □ Got database connection string
echo □ Got Redis connection details
echo □ Copied Application Insights key
echo □ Applied environment variables
echo □ Restarted App Service
echo □ Tested health endpoint
echo □ Verified frontend loads
echo.

echo 🔧 ENVIRONMENT VARIABLE FORMAT:
echo ==============================
echo Copy these to Azure Portal ^> App Service ^> Configuration ^> Application Settings:
echo.
echo DATABASE_URL=postgresql://dbadmin:[PASSWORD]@[SERVER].postgres.database.azure.com:5432/whitelabel_chat?sslmode=require
echo REDIS_URL=redis://:[PRIMARY_KEY]@[REDIS_NAME].redis.cache.windows.net:6380/0?ssl_cert_reqs=required
echo APPINSIGHTS_INSTRUMENTATIONKEY=[INSTRUMENTATION_KEY]
echo.

echo 🚀 AFTER CONFIGURATION:
echo =======================
echo 1. Save all environment variables in Azure Portal
echo 2. Restart your App Service
echo 3. Run: azure-post-deploy.bat to test everything
echo 4. Initialize database if needed
echo.

echo 📞 NEED HELP?
echo =============
echo - Check AZURE_DEPLOYMENT_GUIDE.md for detailed instructions
echo - Use deployment-status.html to test your endpoints
echo - Run azure-post-deploy.bat after configuration
echo.

pause
