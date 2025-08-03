@echo off
setlocal

REM Production Deployment Script for Windows
REM This script sets up your white-label chat platform for production

echo 🚀 White-Label Chat Production Deployment
echo ==========================================

REM Check dependencies
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is required but not installed. Please install Docker Desktop.
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is required but not installed. Please install Docker Desktop.
    exit /b 1
)

echo ✅ Dependencies check passed

REM Create necessary directories
echo 📁 Creating directories...
if not exist logs\nginx mkdir logs\nginx
if not exist backups mkdir backups
if not exist nginx\ssl mkdir nginx\ssl
if not exist data\postgres mkdir data\postgres
if not exist data\redis mkdir data\redis

REM Generate secure keys if they don't exist
if not exist .env.production (
    echo 🔐 Generating production environment file...
    copy .env.production.example .env.production

    REM Generate secret keys using Python
    for /f %%i in ('python -c "import secrets; print(secrets.token_hex(32))"') do set SECRET_KEY=%%i
    for /f %%i in ('python -c "import secrets; print(secrets.token_hex(32))"') do set JWT_SECRET_KEY=%%i
    for /f %%i in ('python -c "import secrets; print(secrets.token_urlsafe(16))"') do set POSTGRES_PASSWORD=%%i

    REM Add to .env.production
    echo SECRET_KEY=%SECRET_KEY% >> .env.production
    echo JWT_SECRET_KEY=%JWT_SECRET_KEY% >> .env.production
    echo POSTGRES_PASSWORD=%POSTGRES_PASSWORD% >> .env.production

    echo ✅ Generated .env.production with secure keys
    echo ⚠️  IMPORTANT: Review and update .env.production with your specific values!
) else (
    echo ✅ Found existing .env.production
)

REM Create Nginx configuration if it doesn't exist
if not exist nginx\nginx.conf (
    echo 🌐 Creating Nginx configuration...
    (
        echo events {
        echo     worker_connections 1024;
        echo }
        echo.
        echo http {
        echo     upstream app {
        echo         server app:5000;
        echo     }
        echo.    
        echo     # HTTP redirect to HTTPS
        echo     server {
        echo         listen 80;
        echo         server_name _;
        echo         return 301 https://$server_name$request_uri;
        echo     }
        echo.    
        echo     # HTTPS server
        echo     server {
        echo         listen 443 ssl http2;
        echo         server_name _;
        echo.        
        echo         # SSL configuration
        echo         ssl_certificate /etc/nginx/ssl/cert.pem;
        echo         ssl_certificate_key /etc/nginx/ssl/key.pem;
        echo.        
        echo         # Security headers
        echo         add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        echo         add_header X-Content-Type-Options "nosniff" always;
        echo         add_header X-Frame-Options "DENY" always;
        echo         add_header X-XSS-Protection "1; mode=block" always;
        echo.        
        echo         # Proxy to Flask app
        echo         location / {
        echo             proxy_pass http://app;
        echo             proxy_set_header Host $host;
        echo             proxy_set_header X-Real-IP $remote_addr;
        echo             proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        echo             proxy_set_header X-Forwarded-Proto $scheme;
        echo         }
        echo.        
        echo         # WebSocket support
        echo         location /socket.io/ {
        echo             proxy_pass http://app;
        echo             proxy_http_version 1.1;
        echo             proxy_set_header Upgrade $http_upgrade;
        echo             proxy_set_header Connection "upgrade";
        echo         }
        echo     }
        echo }
    ) > nginx\nginx.conf
    echo ✅ Created nginx\nginx.conf
)

REM Build and start services
echo 🏗️  Building Docker images...
docker-compose -f docker-compose.prod.yml build

if %errorlevel% neq 0 (
    echo ❌ Docker build failed
    exit /b 1
)

echo 🚀 Starting production services...
docker-compose -f docker-compose.prod.yml up -d

if %errorlevel% neq 0 (
    echo ❌ Failed to start services
    exit /b 1
)

echo.
echo 🎉 Production deployment complete!
echo.
echo 📋 Next Steps:
echo 1. 🔐 Update .env.production with your specific values
echo 2. 🌐 Add your SSL certificates to nginx\ssl\
echo 3. 🗄️  Configure your domain DNS to point to this server
echo 4. 📊 Set up monitoring (Sentry, etc.)
echo 5. 🔄 Configure automated backups
echo.
echo 📊 Service Status:
docker-compose -f docker-compose.prod.yml ps
echo.
echo 🔗 Access your application:
echo    HTTP:  http://localhost
echo    HTTPS: https://localhost (after SSL setup)
echo    API:   https://localhost/api/health
echo.
echo 📝 View logs:
echo    docker-compose -f docker-compose.prod.yml logs -f
echo.
echo 🛑 Stop services:
echo    docker-compose -f docker-compose.prod.yml down

pause
