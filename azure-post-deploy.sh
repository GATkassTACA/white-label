#!/bin/bash

# Azure Post-Deployment Configuration Script
# Run this after your Azure deployment completes successfully

echo "🎉 Azure White Label Chat - Post-Deployment Setup"
echo "=================================================="

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get Azure app details
echo
print_step "Please provide your Azure deployment details:"
read -p "Enter your App Service name (e.g., white-label-chat-app-xyz): " APP_NAME
read -p "Enter your Resource Group name (default: white-label-rg): " RESOURCE_GROUP
RESOURCE_GROUP=${RESOURCE_GROUP:-white-label-rg}

# Construct URLs
APP_URL="https://${APP_NAME}.azurewebsites.net"
HEALTH_URL="${APP_URL}/api/health"
FRONTEND_URL="${APP_URL}/app/"

echo
print_step "Your app URLs:"
echo "Application: $APP_URL"
echo "Health Check: $HEALTH_URL"
echo "Frontend: $FRONTEND_URL"

# Test basic connectivity
echo
print_step "Testing basic connectivity..."

# Test if app is reachable
if curl -s --head "$APP_URL" | head -n 1 | grep -q "200 OK\|404 Not Found\|500 Internal Server Error"; then
    print_success "App service is reachable"
else
    print_error "App service is not reachable. Please check deployment status."
    exit 1
fi

# Test health endpoint
echo
print_step "Testing health endpoint..."
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL" || echo "000")

case $HEALTH_STATUS in
    200)
        print_success "Health check passed! App is fully operational."
        ;;
    503)
        print_warning "Health check returned 503 (Service Unavailable). This is expected if database/Redis aren't configured yet."
        ;;
    404)
        print_warning "Health endpoint not found. The health route may not be registered."
        ;;
    000)
        print_error "Could not connect to health endpoint."
        ;;
    *)
        print_warning "Health check returned status code: $HEALTH_STATUS"
        ;;
esac

# Database setup check
echo
print_step "Checking database configuration..."

if [ "$HEALTH_STATUS" = "503" ]; then
    echo "Database needs configuration. Here are the next steps:"
    echo
    echo "1. Go to Azure Portal > $APP_NAME > Configuration > Application Settings"
    echo "2. Add/verify these environment variables:"
    echo "   - DATABASE_URL=postgresql://[user]:[password]@[server].postgres.database.azure.com:5432/whitelabel_chat?sslmode=require"
    echo "   - REDIS_URL=redis://:[key]@[redis-name].redis.cache.windows.net:6380/0?ssl_cert_reqs=required"
    echo "   - SECRET_KEY=[generate-a-secure-key]"
    echo "   - FLASK_ENV=production"
    echo
    echo "3. Initialize the database:"
    echo "   - Go to Development Tools > SSH"
    echo "   - Run: python -c \"from app import create_app; from app.extensions import db; app=create_app(); app.app_context().push(); db.create_all(); print('Database initialized!')\""
fi

# Generate secure keys
echo
print_step "Generating secure configuration keys..."

SECRET_KEY=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
CSRF_SECRET=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)

echo "Generated secure keys (save these):"
echo "SECRET_KEY=$SECRET_KEY"
echo "WTF_CSRF_SECRET_KEY=$CSRF_SECRET"

# Create environment variables template
cat > azure-app-settings.txt << EOF
# Azure App Service Environment Variables
# Copy these to Azure Portal > App Service > Configuration > Application Settings

FLASK_ENV=production
SECRET_KEY=$SECRET_KEY
WTF_CSRF_SECRET_KEY=$CSRF_SECRET
WEBSITES_PORT=5000
SCM_DO_BUILD_DURING_DEPLOYMENT=true

# Security Settings
WTF_CSRF_ENABLED=True
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
FORCE_HTTPS=True

# Database (replace with your actual values)
DATABASE_URL=postgresql://dbadmin:YOUR_DB_PASSWORD@YOUR_DB_SERVER.postgres.database.azure.com:5432/whitelabel_chat?sslmode=require

# Redis (replace with your actual values)
REDIS_URL=redis://:YOUR_REDIS_KEY@YOUR_REDIS_NAME.redis.cache.windows.net:6380/0?ssl_cert_reqs=required

# Rate Limiting
RATELIMIT_STORAGE_URL=redis://:YOUR_REDIS_KEY@YOUR_REDIS_NAME.redis.cache.windows.net:6380/1?ssl_cert_reqs=required
RATELIMIT_DEFAULT=1000 per hour

# Email (optional - configure with SendGrid)
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
MAIL_DEFAULT_SENDER=noreply@yourdomain.com

# File uploads
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=/tmp/uploads

# Logging
LOG_LEVEL=INFO
LOG_TO_STDOUT=True
EOF

print_success "Created azure-app-settings.txt with all required environment variables"

# Test frontend
echo
print_step "Testing frontend..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" || echo "000")

if [ "$FRONTEND_STATUS" = "200" ]; then
    print_success "Frontend is accessible!"
else
    print_warning "Frontend returned status: $FRONTEND_STATUS"
fi

# Final summary
echo
echo "🎯 Configuration Summary"
echo "========================"
echo "App URL: $APP_URL"
echo "Health Status: $HEALTH_STATUS"
echo "Frontend Status: $FRONTEND_STATUS"
echo
echo "📁 Files Created:"
echo "- azure-app-settings.txt (environment variables)"
echo
echo "🔧 Next Steps:"
echo "1. Apply environment variables from azure-app-settings.txt"
echo "2. Get your database and Redis connection strings from Azure Portal"
echo "3. Initialize database tables"
echo "4. Test all functionality"
echo
echo "🚀 Once configured, your app will be live at:"
echo "$APP_URL"

# Optional: Open browser
read -p "Open the app in browser? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v xdg-open > /dev/null; then
        xdg-open "$APP_URL"
    elif command -v open > /dev/null; then
        open "$APP_URL"
    else
        echo "Please open: $APP_URL"
    fi
fi

print_success "Post-deployment setup completed!"
