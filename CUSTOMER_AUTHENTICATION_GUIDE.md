# PharmAssist Multi-Tenant Authentication & Customer Management System

## 🏥 Overview

This system allows you to sell PharmAssist access to multiple pharmacy customers, each with their own branded login portal, user management, and isolated data.

## 🎯 Key Features

### 1. Multi-Tenant Architecture
- **Isolated Data**: Each pharmacy's data is completely separate
- **Branded Portals**: Custom logos, colors, and subdomains
- **Subscription Management**: Different plans and feature sets
- **Usage Tracking**: Analytics and billing data per customer

### 2. Customer Onboarding
- **Automated Setup**: Generate complete customer packages
- **Branded Login Pages**: Custom pharmacy branding
- **QR Code Access**: Mobile-friendly login
- **Setup Instructions**: Complete onboarding documentation

### 3. Authentication Features
- **Secure Login**: Password hashing and session management
- **Account Lockout**: Protection against brute force attacks
- **Password Reset**: Self-service password recovery
- **Session Tracking**: Audit logs and security monitoring

## 🚀 Quick Start Guide

### Step 1: Set Up the Database

The system automatically creates these tables:
- `tenants` - Pharmacy organizations
- `users` - Individual user accounts
- `user_sessions` - Active login sessions
- `audit_log` - Security and usage tracking

### Step 2: Create Your First Customer

#### Option A: Use the Web Interface
```bash
# Access the admin portal
https://vitalcare.azurewebsites.net/admin/create-customer
```

#### Option B: Use the Command Line Script
```bash
python generate_customers.py
```

#### Option C: Use the API
```python
from customer_onboarding import CustomerOnboarding

onboarding = CustomerOnboarding(db_connection)
result = onboarding.generate_customer_package({
    'pharmacy_name': 'Sunshine Pharmacy',
    'contact_email': 'manager@sunshine.com',
    'subdomain': 'sunshine',
    'plan': 'professional',
    'brand_color': '#f59e0b'
})
```

### Step 3: Customer Access

Each customer gets:
1. **Branded Login URL**: `https://vitalcare.azurewebsites.net/login/sunshine`
2. **Admin Credentials**: Username and temporary password
3. **Setup Instructions**: Complete onboarding guide
4. **QR Code**: Mobile access
5. **API Key**: For enterprise customers

## 💼 Subscription Plans

### Trial Plan ($0/month)
- 100 PDFs per month
- Basic processing
- 30-day trial
- Email support

### Professional Plan ($99/month)
- 2,000 PDFs per month
- OCR processing
- Custom branding
- Analytics dashboard
- Phone support

### Enterprise Plan ($299/month)
- Unlimited PDFs
- API access
- Dedicated support
- SLA guarantee
- Advanced analytics

## 🔐 Security Features

### Authentication
- **Password Hashing**: Industry-standard bcrypt
- **Session Tokens**: Secure, time-limited sessions
- **Account Lockout**: 5 failed attempts = 30-minute lockout
- **HTTPS Only**: All communications encrypted

### Authorization
- **Role-Based Access**: Admin, user, and read-only roles
- **Tenant Isolation**: Users can only access their pharmacy's data
- **API Rate Limiting**: Prevents abuse
- **Audit Logging**: Complete activity tracking

### HIPAA Compliance
- **Data Encryption**: At rest and in transit
- **Access Logs**: Who accessed what and when
- **Session Timeouts**: Automatic logout
- **Secure Deletion**: Complete data removal on request

## 📊 Customer Management

### Adding New Customers

1. **Collect Information**:
   - Pharmacy name and contact details
   - Desired subdomain (optional)
   - Logo and brand colors
   - Subscription plan
   - Admin user details

2. **Generate Package**:
   - Creates tenant record
   - Sets up admin user
   - Generates secure credentials
   - Creates branded login portal

3. **Deliver Credentials**:
   - Secure credential delivery
   - Setup instructions
   - Support contact information

### Managing Existing Customers

#### Update Subscription
```python
# Upgrade customer plan
user_manager.update_tenant_subscription(tenant_id, 'enterprise')

# Extend subscription
new_expiry = datetime.now() + timedelta(days=365)
user_manager.extend_subscription(tenant_id, new_expiry)
```

#### Suspend Customer
```python
# Temporarily disable access
user_manager.suspend_tenant(tenant_id)

# Reactivate
user_manager.activate_tenant(tenant_id)
```

#### Usage Analytics
```python
# Get processing statistics
stats = user_manager.get_tenant_usage(tenant_id, last_30_days=True)
print(f"PDFs processed: {stats['pdf_count']}")
print(f"Total users: {stats['user_count']}")
```

## 🎨 Branding Customization

### Logo Integration
- Upload pharmacy logo to cloud storage
- Reference logo URL in tenant record
- Automatic scaling and optimization

### Color Schemes
- Primary color (buttons, headers)
- Secondary color (backgrounds)
- CSS custom properties for consistency

### Custom Subdomains
- Format: `https://vitalcare.azurewebsites.net/login/[subdomain]`
- Automatic SSL certificates
- Brand-consistent URLs

## 📱 Mobile Access

### QR Code Generation
- Automatic QR code creation for each customer
- Contains branded login URL
- Optimized for pharmacy staff mobile access

### Responsive Design
- Mobile-first interface
- Touch-friendly controls
- Tablet optimization

## 🔧 API Access (Enterprise)

### Authentication
```python
import requests

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# Process PDF via API
response = requests.post(
    'https://vitalcare.azurewebsites.net/api/process',
    headers=headers,
    files={'pdf': open('medication_list.pdf', 'rb')}
)
```

### Endpoints
- `POST /api/process` - Process PDF document
- `GET /api/history` - Get processing history
- `GET /api/usage` - Get usage statistics
- `POST /api/users` - Create new user

## 📈 Analytics & Reporting

### Customer Dashboard
- Monthly processing volume
- User activity statistics
- Popular processing methods
- Error rates and resolution

### Admin Dashboard
- Revenue tracking
- Customer usage patterns
- Support ticket volume
- System performance metrics

## 💰 Billing Integration

### Subscription Tracking
- Automatic renewal dates
- Usage-based billing alerts
- Plan upgrade notifications
- Payment failure handling

### Revenue Analytics
- Monthly recurring revenue (MRR)
- Customer lifetime value (CLV)
- Churn rate tracking
- Plan distribution analysis

## 🛟 Support System

### Tiered Support
- **Basic**: Email support, knowledge base
- **Professional**: Phone + email support
- **Enterprise**: Dedicated account manager

### Support Portal Integration
- Automatic ticket creation
- Customer context sharing
- Escalation procedures
- SLA tracking

## 🚀 Deployment Checklist

### Production Setup
- [ ] Database with SSL connections
- [ ] Redis cache for sessions
- [ ] SMTP server for emails
- [ ] SSL certificates configured
- [ ] Backup procedures in place
- [ ] Monitoring and alerting
- [ ] HIPAA compliance review

### Customer Onboarding Process
- [ ] Lead qualification
- [ ] Contract signing
- [ ] Technical setup
- [ ] Credential delivery
- [ ] Training session
- [ ] Go-live support

## 📞 Next Steps

1. **Deploy the Authentication System**: Add user management to your existing PharmAssist
2. **Create Your First Customer**: Use the provided tools to onboard a test pharmacy
3. **Test the Branded Experience**: Verify the custom login portal works
4. **Set Up Billing**: Integrate with your preferred payment processor
5. **Launch Marketing**: Start selling PharmAssist to pharmacies!

## 🎉 Success Metrics

Track these KPIs for your PharmAssist business:
- **Customer Acquisition**: New pharmacy signups per month
- **Monthly Recurring Revenue**: Predictable subscription income
- **Customer Satisfaction**: Support ticket resolution time
- **Product Usage**: PDFs processed per customer
- **Retention Rate**: Customer churn and renewal rates

---

**Ready to sell PharmAssist to pharmacies?** 
Start with the customer generation script and create your first branded pharmacy portal! 🏥✨
