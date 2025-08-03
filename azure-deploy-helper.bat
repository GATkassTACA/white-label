@echo off
echo ========================================
echo Azure Deployment Helper for White Label Chat
echo ========================================
echo.
echo Since you're already signed into Azure Portal, here are the next steps:
echo.
echo 1. CREATE WEB APP:
echo    - Go to Azure Portal: https://portal.azure.com
echo    - Click "Create a resource" ^> "Web App"
echo    - Resource Group: white-label-rg
echo    - Name: white-label-chat-app-[your-initials]
echo    - Runtime: Python 3.11
echo    - OS: Linux
echo    - Plan: B1 Basic
echo.
echo 2. CREATE DATABASE:
echo    - Create resource ^> "Azure Database for PostgreSQL"
echo    - Choose "Flexible Server"
echo    - Resource Group: white-label-rg
echo    - Server name: white-label-db-[your-initials]
echo    - Version: PostgreSQL 15
echo    - Admin: dbadmin
echo    - Create strong password!
echo.
echo 3. CREATE REDIS:
echo    - Create resource ^> "Azure Cache for Redis"
echo    - Resource Group: white-label-rg
echo    - Name: white-label-redis-[your-initials]
echo    - Type: Basic C0
echo.
echo 4. CONFIGURE ENVIRONMENT:
echo    After resources are created, we'll configure the app settings
echo    with database and Redis connection strings.
echo.
echo 5. DEPLOY CODE:
echo    We'll set up GitHub deployment or local Git push.
echo.
echo ========================================
echo Press any key when you've created the resources...
pause

echo.
echo Great! Now let's get your connection strings.
echo.
echo Please provide the following from Azure Portal:
echo.
set /p WEB_APP_NAME="Web App Name: "
set /p DB_SERVER_NAME="Database Server Name: "
set /p DB_PASSWORD="Database Password: "
set /p REDIS_NAME="Redis Cache Name: "
echo.

echo Creating environment configuration...

(
echo # Azure Environment Configuration
echo FLASK_ENV=production
echo SECRET_KEY=%RANDOM%%RANDOM%%RANDOM%%RANDOM%
echo DATABASE_URL=postgresql://dbadmin:%DB_PASSWORD%@%DB_SERVER_NAME%.postgres.database.azure.com:5432/whitelabel_chat?sslmode=require
echo REDIS_URL=redis://:%REDIS_KEY%@%REDIS_NAME%.redis.cache.windows.net:6380/0?ssl_cert_reqs=required
echo WEBSITES_PORT=5000
echo SCM_DO_BUILD_DURING_DEPLOYMENT=true
echo WTF_CSRF_ENABLED=True
echo SESSION_COOKIE_SECURE=True
echo SESSION_COOKIE_HTTPONLY=True
echo FORCE_HTTPS=True
) > .env.azure

echo.
echo ✅ Environment file created: .env.azure
echo.
echo NEXT STEPS:
echo 1. Go to your Web App in Azure Portal
echo 2. Navigate to Configuration ^> Application settings
echo 3. Add the environment variables from .env.azure
echo 4. Set up deployment from GitHub or local Git
echo.
echo Your app will be available at:
echo https://%WEB_APP_NAME%.azurewebsites.net
echo.
pause
