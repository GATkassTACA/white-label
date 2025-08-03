#!/bin/bash

# Production Deployment Script
# This script sets up your white-label chat platform for production

set -e

echo "🚀 White-Label Chat Production Deployment"
echo "=========================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root"
   exit 1
fi

# Check dependencies
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed. Aborting." >&2; exit 1; }

echo "✅ Dependencies check passed"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs/nginx
mkdir -p backups
mkdir -p nginx/ssl
mkdir -p data/postgres
mkdir -p data/redis

# Generate secure keys if they don't exist
if [ ! -f .env.production ]; then
    echo "🔐 Generating production environment file..."
    cp .env.production.example .env.production
    
    # Generate secret keys
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    POSTGRES_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))")
    
    # Replace placeholders
    sed -i "s/REPLACE_WITH_64_CHAR_SECRET_KEY/$SECRET_KEY/g" .env.production
    sed -i "s/REPLACE_WITH_64_CHAR_JWT_SECRET_KEY/$JWT_SECRET_KEY/g" .env.production
    
    echo "SECRET_KEY=$SECRET_KEY" >> .env.production
    echo "JWT_SECRET_KEY=$JWT_SECRET_KEY" >> .env.production
    echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD" >> .env.production
    
    echo "✅ Generated .env.production with secure keys"
    echo "⚠️  IMPORTANT: Review and update .env.production with your specific values!"
else
    echo "✅ Found existing .env.production"
fi

# Create Nginx configuration if it doesn't exist
if [ ! -f nginx/nginx.conf ]; then
    echo "🌐 Creating Nginx configuration..."
    cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:5000;
    }
    
    # HTTP redirect to HTTPS
    server {
        listen 80;
        server_name _;
        return 301 https://$server_name$request_uri;
    }
    
    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name _;
        
        # SSL configuration (update paths for your certificates)
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        
        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-Frame-Options "DENY" always;
        add_header X-XSS-Protection "1; mode=block" always;
        
        # Proxy to Flask app
        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # WebSocket support for Socket.IO
        location /socket.io/ {
            proxy_pass http://app;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF
    echo "✅ Created nginx/nginx.conf"
    echo "⚠️  IMPORTANT: Update SSL certificate paths in nginx/nginx.conf"
fi

# Build and start services
echo "🏗️  Building Docker images..."
docker-compose -f docker-compose.prod.yml build

echo "🚀 Starting production services..."
docker-compose -f docker-compose.prod.yml up -d

echo ""
echo "🎉 Production deployment complete!"
echo ""
echo "📋 Next Steps:"
echo "1. 🔐 Update .env.production with your specific values"
echo "2. 🌐 Add your SSL certificates to nginx/ssl/"
echo "3. 🗄️  Configure your domain DNS to point to this server"
echo "4. 📊 Set up monitoring (Sentry, etc.)"
echo "5. 🔄 Configure automated backups"
echo ""
echo "📊 Service Status:"
docker-compose -f docker-compose.prod.yml ps
echo ""
echo "🔗 Access your application:"
echo "   HTTP:  http://localhost"
echo "   HTTPS: https://localhost (after SSL setup)"
echo "   API:   https://localhost/api/health"
echo ""
echo "📝 View logs:"
echo "   docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose -f docker-compose.prod.yml down"
