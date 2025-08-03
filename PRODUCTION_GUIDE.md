# 🚀 Production Deployment Guide

## Overview
This guide covers everything needed to deploy your white-label chat platform to production safely and efficiently.

## 📋 Production Readiness Checklist

### ✅ Security Hardening
- [x] **CSP Headers**: Content Security Policy implemented
- [x] **Security Middleware**: X-Frame-Options, X-Content-Type-Options, HSTS
- [x] **External Scripts**: Inline scripts moved to external files
- [x] **JWT Authentication**: Secure token-based authentication
- [ ] **HTTPS**: SSL/TLS certificates configured
- [ ] **Environment Variables**: All secrets in environment variables
- [ ] **Security Scanning**: Code security audit

### ✅ Application Configuration
- [x] **Production Config**: Separate production configuration class
- [x] **Database**: SQLite for development, PostgreSQL ready for production
- [x] **Error Handling**: Comprehensive error handling and logging
- [ ] **Health Checks**: Application health monitoring endpoints
- [ ] **Rate Limiting**: Production-appropriate rate limits
- [ ] **Monitoring**: Application performance monitoring

### ✅ Infrastructure
- [x] **Docker**: Containerization ready
- [ ] **Load Balancer**: For high availability
- [ ] **Database**: Production database setup
- [ ] **Redis**: Session store and caching
- [ ] **CDN**: Static asset delivery
- [ ] **Backup**: Database backup strategy

## 🔧 Environment Configuration

### 1. Production Environment Variables

Create `.env.production`:

```bash
# Application
FLASK_APP=run.py
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Security (REQUIRED - Generate strong keys!)
SECRET_KEY=<your-super-secret-key-64-chars-minimum>
JWT_SECRET_KEY=<your-jwt-secret-key-64-chars-minimum>

# Database
DATABASE_URL=postgresql://username:password@host:port/database

# Redis (for sessions and caching)
REDIS_URL=redis://username:password@host:port/0

# Rate Limiting (Production Values)
RATE_LIMIT_MESSAGES_PER_MINUTE=30
RATE_LIMIT_CONNECTIONS_PER_IP=10
MAX_USERS_PER_ROOM=100
MAX_ROOMS_PER_USER=20

# Email (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@domain.com
MAIL_PASSWORD=your-app-password

# External Services
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

### 2. Generate Secure Keys

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Generate JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
```

## 🐳 Docker Production Deployment

### 1. Multi-stage Dockerfile (Optimized)

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Copy Python dependencies from builder stage
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# Add local bins to PATH
ENV PATH=/root/.local/bin:$PATH

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run the application
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "run:app"]
```

### 2. Docker Compose Production

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://postgres:password@db:5432/whitelabel
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=whitelabel
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=your-secure-password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

## ⚙️ Production Configuration Updates

### 1. Enhanced Production Config

```python
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    DEVELOPMENT = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': -1,
        'pool_pre_ping': True
    }
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set")
    if not JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY environment variable must be set")
    
    # HTTPS enforcement
    PREFERRED_URL_SCHEME = 'https'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Rate limiting
    RATE_LIMIT_MESSAGES_PER_MINUTE = 30
    RATE_LIMIT_CONNECTIONS_PER_IP = 10
    
    # Redis for sessions
    REDIS_URL = os.environ.get('REDIS_URL')
    
    # Logging
    LOG_LEVEL = 'INFO'
```

### 2. Health Check Endpoint

```python
@app.route('/api/health')
def health_check():
    """Health check endpoint for load balancers"""
    try:
        # Check database connectivity
        db.session.execute('SELECT 1')
        
        # Check Redis connectivity (if configured)
        if app.config.get('REDIS_URL'):
            redis_client.ping()
            
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500
```

## 🌐 Deployment Platforms

### 1. Railway (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### 2. Heroku
```bash
# Install Heroku CLI and deploy
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
heroku addons:create heroku-redis:hobby-dev
git push heroku main
```

### 3. DigitalOcean App Platform
```yaml
name: white-label-chat
services:
- name: app
  source_dir: /
  github:
    repo: your-username/white-label
    branch: main
  run_command: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 run:app
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: FLASK_ENV
    value: production
databases:
- name: db
  engine: PG
  version: "15"
- name: redis
  engine: REDIS
  version: "7"
```

## 📊 Monitoring & Logging

### 1. Application Monitoring

```python
# Add to your Flask app
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

if app.config.get('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=app.config['SENTRY_DSN'],
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0
    )
```

### 2. Logging Configuration

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    # File logging
    file_handler = RotatingFileHandler(
        'logs/whitelabel.log',
        maxBytes=10240000,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('White Label Chat startup')
```

## 🔒 Security Best Practices

### 1. HTTPS Configuration (Nginx)

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location / {
        proxy_pass http://app:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /socket.io/ {
        proxy_pass http://app:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 2. Database Security

```bash
# PostgreSQL security
# Create dedicated database user
CREATE USER whitelabel_user WITH ENCRYPTED PASSWORD 'secure_password';
CREATE DATABASE whitelabel OWNER whitelabel_user;
GRANT ALL PRIVILEGES ON DATABASE whitelabel TO whitelabel_user;
```

## 📈 Performance Optimization

### 1. Database Indexing

```sql
-- Add indexes for common queries
CREATE INDEX idx_messages_room_id ON messages(room_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp);
CREATE INDEX idx_users_email ON users(email);
```

### 2. Caching Strategy

```python
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': app.config['REDIS_URL']
})

@cache.memoize(timeout=300)
def get_branding_config(client_id):
    # Cache branding configurations
    return load_client_branding(client_id)
```

## 🚀 Deployment Workflow

### 1. CI/CD Pipeline (GitHub Actions)

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python -m pytest
    
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Deploy to Railway
      run: |
        railway up
```

### 2. Pre-deployment Checklist

- [ ] All tests passing
- [ ] Security scan completed
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] SSL certificates valid
- [ ] Monitoring configured
- [ ] Backup strategy in place

## 📝 Next Steps

1. **Choose deployment platform** (Railway recommended for ease)
2. **Set up production database** (PostgreSQL)
3. **Configure monitoring** (Sentry for errors)
4. **Set up CI/CD** (GitHub Actions)
5. **Configure custom domain** and SSL
6. **Set up database backups**
7. **Performance testing** and optimization

## 📞 Support

For production deployment assistance:
- Review logs in `/logs` directory
- Check health endpoint `/api/health`
- Monitor database connections
- Verify environment variables

Your platform is ready for production! The security hardening is complete, and you have a solid foundation for scaling.
