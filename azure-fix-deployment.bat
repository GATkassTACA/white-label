@echo off
echo 🔧 Azure Deployment - Fix for Private Endpoint Error
echo ===================================================
echo.
echo The deployment failed due to a subnet delegation conflict.
echo Let's redeploy with a simpler, more reliable configuration.
echo.

set /p CONTINUE="Continue with fixed deployment? (y/N): "
if /i not "!CONTINUE!"=="y" (
    echo Deployment cancelled.
    pause
    exit /b 0
)

echo.
echo 🔧 Creating fixed Azure resources...
echo.

REM Clean up failed deployment first
echo 1. Cleaning up failed deployment...
echo Go to Azure Portal ^> Resource Groups ^> white-label-rg
echo Click "Delete resource group" to clean up failed resources
echo.
pause

echo.
echo 2. Creating new deployment with fixed configuration...
echo.

REM Simple resource creation commands
echo Copy and run these commands in Azure Cloud Shell:
echo.
echo # Create resource group
echo az group create --name white-label-rg-v2 --location "East US"
echo.
echo # Create App Service plan
echo az appservice plan create \
echo   --resource-group white-label-rg-v2 \
echo   --name white-label-plan \
echo   --location "East US" \
echo   --sku B1 \
echo   --is-linux
echo.
echo # Create Web App
echo az webapp create \
echo   --resource-group white-label-rg-v2 \
echo   --plan white-label-plan \
echo   --name white-label-chat-app-%RANDOM% \
echo   --runtime "PYTHON:3.11"
echo.
echo # Create PostgreSQL with PUBLIC access ^(no private endpoints^)
echo az postgres flexible-server create \
echo   --resource-group white-label-rg-v2 \
echo   --name white-label-db-%RANDOM% \
echo   --location "East US" \
echo   --admin-user dbadmin \
echo   --admin-password "%RANDOM%%RANDOM%Pass!" \
echo   --sku-name Standard_B1ms \
echo   --tier Burstable \
echo   --version 15 \
echo   --public-access 0.0.0.0-255.255.255.255
echo.
echo # Create Redis
echo az redis create \
echo   --resource-group white-label-rg-v2 \
echo   --name white-label-redis-%RANDOM% \
echo   --location "East US" \
echo   --sku Basic \
echo   --vm-size c0
echo.

echo 📋 Next steps:
echo 1. Delete the failed resource group in Azure Portal
echo 2. Run the commands above in Azure Cloud Shell
echo 3. Configure environment variables
echo 4. Deploy your code
echo.
pause
