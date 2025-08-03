@echo off
setlocal enabledelayedexpansion

REM Azure Post-Deployment Configuration Script (Windows)
REM Run this after your Azure deployment completes successfully

echo 🎉 Azure White Label Chat - Post-Deployment Setup
echo ==================================================
echo.

REM Get Azure app details
set /p APP_NAME="Enter your App Service name (e.g., white-label-chat-app-xyz): "
set /p RESOURCE_GROUP="Enter your Resource Group name (default: white-label-rg): "
if "!RESOURCE_GROUP!"=="" set RESOURCE_GROUP=white-label-rg

REM Construct URLs
set APP_URL=https://!APP_NAME!.azurewebsites.net
set HEALTH_URL=!APP_URL!/api/health
set FRONTEND_URL=!APP_URL!/app/

echo.
echo ℹ️  Your app URLs:
echo Application: !APP_URL!
echo Health Check: !HEALTH_URL!
echo Frontend: !FRONTEND_URL!
echo.

REM Test basic connectivity
echo ℹ️  Testing connectivity...

REM Test health endpoint using PowerShell
powershell -Command "try { $response = Invoke-WebRequest -Uri '!HEALTH_URL!' -UseBasicParsing -ErrorAction SilentlyContinue; $response.StatusCode } catch { $_.Exception.Response.StatusCode.Value__ }" > temp_health_status.txt
set /p HEALTH_STATUS=<temp_health_status.txt
del temp_health_status.txt

if "!HEALTH_STATUS!"=="200" (
    echo ✅ SUCCESS: Health check passed! App is fully operational.
) else if "!HEALTH_STATUS!"=="503" (
    echo ⚠️  WARNING: Health check returned 503. Database/Redis configuration needed.
) else if "!HEALTH_STATUS!"=="404" (
    echo ⚠️  WARNING: Health endpoint not found. Route may not be registered.
) else (
    echo ⚠️  WARNING: Health check returned status: !HEALTH_STATUS!
)

echo.
echo ℹ️  Generating secure configuration keys...

REM Generate secure keys using PowerShell
for /f %%i in ('powershell -Command "[System.Web.Security.Membership]::GeneratePassword(32, 8)"') do set SECRET_KEY=%%i
for /f %%i in ('powershell -Command "[System.Web.Security.Membership]::GeneratePassword(32, 8)"') do set CSRF_SECRET=%%i

echo Generated secure keys (save these):
echo SECRET_KEY=!SECRET_KEY!
echo WTF_CSRF_SECRET_KEY=!CSRF_SECRET!
echo.

REM Create environment variables template
echo ℹ️  Creating environment variables template...

(
echo # Azure App Service Environment Variables
echo # Copy these to Azure Portal ^> App Service ^> Configuration ^> Application Settings
echo.
echo FLASK_ENV=production
echo SECRET_KEY=!SECRET_KEY!
echo WTF_CSRF_SECRET_KEY=!CSRF_SECRET!
echo WEBSITES_PORT=5000
echo SCM_DO_BUILD_DURING_DEPLOYMENT=true
echo.
echo # Security Settings
echo WTF_CSRF_ENABLED=True
echo SESSION_COOKIE_SECURE=True
echo SESSION_COOKIE_HTTPONLY=True
echo SESSION_COOKIE_SAMESITE=Lax
echo FORCE_HTTPS=True
echo.
echo # Database ^(replace with your actual values^)
echo DATABASE_URL=postgresql://dbadmin:YOUR_DB_PASSWORD@YOUR_DB_SERVER.postgres.database.azure.com:5432/whitelabel_chat?sslmode=require
echo.
echo # Redis ^(replace with your actual values^)
echo REDIS_URL=redis://:YOUR_REDIS_KEY@YOUR_REDIS_NAME.redis.cache.windows.net:6380/0?ssl_cert_reqs=required
echo.
echo # Rate Limiting
echo RATELIMIT_STORAGE_URL=redis://:YOUR_REDIS_KEY@YOUR_REDIS_NAME.redis.cache.windows.net:6380/1?ssl_cert_reqs=required
echo RATELIMIT_DEFAULT=1000 per hour
echo.
echo # Email ^(optional - configure with SendGrid^)
echo MAIL_SERVER=smtp.sendgrid.net
echo MAIL_PORT=587
echo MAIL_USE_TLS=True
echo MAIL_USERNAME=apikey
echo MAIL_PASSWORD=your-sendgrid-api-key
echo MAIL_DEFAULT_SENDER=noreply@yourdomain.com
echo.
echo # File uploads
echo MAX_CONTENT_LENGTH=16777216
echo UPLOAD_FOLDER=/tmp/uploads
echo.
echo # Logging
echo LOG_LEVEL=INFO
echo LOG_TO_STDOUT=True
) > azure-app-settings.txt

echo ✅ SUCCESS: Created azure-app-settings.txt with all required environment variables
echo.

REM Test frontend
echo ℹ️  Testing frontend...
powershell -Command "try { $response = Invoke-WebRequest -Uri '!FRONTEND_URL!' -UseBasicParsing -ErrorAction SilentlyContinue; $response.StatusCode } catch { $_.Exception.Response.StatusCode.Value__ }" > temp_frontend_status.txt
set /p FRONTEND_STATUS=<temp_frontend_status.txt
del temp_frontend_status.txt

if "!FRONTEND_STATUS!"=="200" (
    echo ✅ SUCCESS: Frontend is accessible!
) else (
    echo ⚠️  WARNING: Frontend returned status: !FRONTEND_STATUS!
)

echo.
echo 🎯 Configuration Summary
echo ========================
echo App URL: !APP_URL!
echo Health Status: !HEALTH_STATUS!
echo Frontend Status: !FRONTEND_STATUS!
echo.
echo 📁 Files Created:
echo - azure-app-settings.txt ^(environment variables^)
echo.
echo 🔧 Next Steps:
echo 1. Apply environment variables from azure-app-settings.txt
echo 2. Get your database and Redis connection strings from Azure Portal
echo 3. Initialize database tables
echo 4. Test all functionality
echo.
echo 🚀 Once configured, your app will be live at:
echo !APP_URL!
echo.

REM Create quick test script
echo ℹ️  Creating quick test script...
(
echo @echo off
echo echo Testing your Azure deployment...
echo echo.
echo echo Health Check:
echo curl -s !HEALTH_URL! ^|^| echo "Health check failed"
echo echo.
echo echo Frontend Test:
echo curl -s -I !FRONTEND_URL! ^|^| echo "Frontend test failed"
echo echo.
echo echo API Test:
echo curl -s !APP_URL!/api/ ^|^| echo "API test failed"
echo pause
) > test-azure-app.bat

echo ✅ SUCCESS: Created test-azure-app.bat for quick testing
echo.

if "!HEALTH_STATUS!"=="503" (
    echo 🔧 DATABASE CONFIGURATION NEEDED:
    echo ================================
    echo Your app is deployed but needs database configuration.
    echo.
    echo Steps to complete setup:
    echo 1. Go to Azure Portal ^> !APP_NAME! ^> Configuration ^> Application Settings
    echo 2. Add environment variables from azure-app-settings.txt
    echo 3. Replace YOUR_DB_PASSWORD, YOUR_DB_SERVER, YOUR_REDIS_KEY, YOUR_REDIS_NAME with actual values
    echo 4. Save and restart the app service
    echo 5. Initialize database: Go to Development Tools ^> SSH and run:
    echo    python -c "from app import create_app; from app.extensions import db; app=create_app(^); app.app_context(^).push(^); db.create_all(^); print('Database initialized!')"
    echo.
)

set /p OPEN_BROWSER="Open the app in browser? (y/N): "
if /i "!OPEN_BROWSER!"=="y" (
    start !APP_URL!
)

echo.
echo ✅ SUCCESS: Post-deployment setup completed!
echo.
echo 📞 Support: If you need help, check the documentation files:
echo - AZURE_DEPLOYMENT_GUIDE.md
echo - AZURE_POST_DEPLOYMENT.md
echo - deployment-status.html
echo.
pause
