# Azure App Service Configuration Guide
# Use this after your Azure deployment completes

## 🎯 Post-Deployment Configuration Steps

### 1. App Service Configuration
Once your Azure deployment finishes, you'll need to configure environment variables:

**Go to Azure Portal > Your App Service > Configuration > Application Settings**

Add these settings:

```
FLASK_ENV=production
SECRET_KEY=your-generated-secret-key-here
WEBSITES_PORT=5000
SCM_DO_BUILD_DURING_DEPLOYMENT=true

# Database (replace with your actual values)
DATABASE_URL=postgresql://dbadmin:YOUR_PASSWORD@YOUR_DB_SERVER.postgres.database.azure.com:5432/whitelabel_chat?sslmode=require

# Redis (replace with your actual values)  
REDIS_URL=redis://:YOUR_REDIS_KEY@YOUR_REDIS_NAME.redis.cache.windows.net:6380/0?ssl_cert_reqs=required

# Security Settings
WTF_CSRF_ENABLED=True
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
FORCE_HTTPS=True

# Email Configuration (optional - configure with SendGrid)
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
MAIL_DEFAULT_SENDER=noreply@yourdomain.com

# Application Insights (auto-configured)
APPINSIGHTS_INSTRUMENTATIONKEY=auto-generated
```

### 2. Database Setup
After deployment, create the database tables:

**Option A: Azure Cloud Shell**
```bash
# Connect to your database and run:
python -c "
from app import create_app
from app.extensions import db
app = create_app()
with app.app_context():
    db.create_all()
    print('Database tables created!')
"
```

**Option B: SSH into App Service**
1. Go to Azure Portal > Your App Service > Development Tools > SSH
2. Run the database initialization commands

### 3. Custom Domain (Optional)
If you have a custom domain:
1. Go to Custom domains in your App Service
2. Add your domain
3. Configure SSL certificate

### 4. Health Check Verification
Your app includes health check endpoints:
- `/api/health` - Overall health status
- `/api/ready` - Readiness probe
- `/api/live` - Liveness probe

Azure App Service will automatically use `/api/health` for monitoring.

### 5. Monitoring Setup
Your deployment includes Application Insights for:
- Performance monitoring
- Error tracking
- User analytics
- Custom telemetry

Access it via: Azure Portal > Your App Service > Application Insights

### 6. Scaling Configuration
For production traffic:
1. Go to Scale up (App Service plan) to upgrade your tier
2. Go to Scale out to configure auto-scaling rules

### 7. Backup Configuration
Set up automated backups:
1. Go to Backups in your App Service
2. Configure backup schedule and retention

## 🚀 Quick Test Commands

After configuration, test your deployment:

```bash
# Health check
curl https://YOUR_APP_NAME.azurewebsites.net/api/health

# Frontend
curl https://YOUR_APP_NAME.azurewebsites.net/app/

# API status
curl https://YOUR_APP_NAME.azurewebsites.net/api/
```

## 🔧 Troubleshooting

**Common Issues:**

1. **502 Bad Gateway**: Check logs in Azure Portal > Log stream
2. **Database Connection**: Verify connection string and firewall rules
3. **Static Files**: Ensure static files are properly served
4. **Environment Variables**: Double-check all required variables are set

**Useful Commands:**
```bash
# View logs
az webapp log tail --name YOUR_APP_NAME --resource-group YOUR_RESOURCE_GROUP

# Restart app
az webapp restart --name YOUR_APP_NAME --resource-group YOUR_RESOURCE_GROUP

# SSH into app
az webapp ssh --name YOUR_APP_NAME --resource-group YOUR_RESOURCE_GROUP
```

## 📊 Performance Optimization

For production:
1. Enable Redis caching
2. Configure CDN for static assets
3. Set up database connection pooling
4. Enable gzip compression
5. Configure caching headers

Your app is now production-ready! 🎉
