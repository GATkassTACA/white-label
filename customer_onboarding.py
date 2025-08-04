import os
import secrets
import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from user_management import UserManager
import qrcode
import io
import base64

class CustomerOnboarding:
    def __init__(self, db_connection):
        self.db = db_connection
        self.user_manager = UserManager(db_connection)
    
    def generate_customer_package(self, customer_data):
        """Generate complete customer setup package"""
        
        # 1. Create tenant
        tenant_result = self.user_manager.create_tenant({
            'tenant_name': customer_data['pharmacy_name'].lower().replace(' ', '_'),
            'display_name': customer_data['pharmacy_name'],
            'subdomain': customer_data.get('subdomain'),
            'logo_url': customer_data.get('logo_url'),
            'primary_color': customer_data.get('brand_color', '#0078d4'),
            'secondary_color': '#ffffff',
            'subscription_type': customer_data.get('plan', 'professional'),
            'subscription_expires': self._calculate_expiry(customer_data.get('plan')),
            'contact_email': customer_data['contact_email'],
            'contact_phone': customer_data.get('phone'),
            'billing_address': customer_data.get('address')
        })
        
        if tenant_result['status'] == 'error':
            return tenant_result
        
        tenant_id = tenant_result['tenant_id']
        api_key = tenant_result['api_key']
        
        # 2. Create admin user
        admin_result = self.user_manager.create_user({
            'username': customer_data['admin_username'],
            'email': customer_data['admin_email'],
            'password': customer_data['admin_password'],
            'first_name': customer_data.get('admin_first_name'),
            'last_name': customer_data.get('admin_last_name'),
            'role': 'admin'
        }, tenant_id)
        
        if admin_result['status'] == 'error':
            return admin_result
        
        # 3. Generate login URLs
        base_url = os.getenv('BASE_URL', 'https://vitalcare.azurewebsites.net')
        if customer_data.get('subdomain'):
            login_url = f"{base_url}/login/{customer_data['subdomain']}"
        else:
            login_url = f"{base_url}/login?tenant={tenant_id}"
        
        # 4. Generate QR code for mobile access
        qr_code = self._generate_qr_code(login_url)
        
        # 5. Create setup package
        setup_package = {
            'tenant_id': tenant_id,
            'pharmacy_name': customer_data['pharmacy_name'],
            'login_url': login_url,
            'api_key': api_key,
            'admin_credentials': {
                'username': customer_data['admin_username'],
                'email': customer_data['admin_email'],
                'temp_password': customer_data['admin_password']
            },
            'qr_code': qr_code,
            'setup_instructions': self._generate_setup_instructions(customer_data, login_url),
            'subscription_details': {
                'plan': customer_data.get('plan', 'professional'),
                'expires': tenant_result.get('subscription_expires'),
                'features': self._get_plan_features(customer_data.get('plan'))
            }
        }
        
        return {
            'status': 'success',
            'package': setup_package
        }
    
    def _calculate_expiry(self, plan):
        """Calculate subscription expiry based on plan"""
        if plan == 'trial':
            return datetime.datetime.now() + datetime.timedelta(days=30)
        elif plan == 'monthly':
            return datetime.datetime.now() + datetime.timedelta(days=30)
        elif plan == 'annual':
            return datetime.datetime.now() + datetime.timedelta(days=365)
        else:  # professional/enterprise
            return datetime.datetime.now() + datetime.timedelta(days=365)
    
    def _generate_qr_code(self, url):
        """Generate QR code for mobile access"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def _get_plan_features(self, plan):
        """Get features for subscription plan"""
        features = {
            'trial': [
                'Process up to 100 PDFs/month',
                'Basic PDF processing',
                'Email support',
                '30-day trial period'
            ],
            'basic': [
                'Process up to 500 PDFs/month',
                'Standard PDF processing',
                'CareTend format conversion',
                'Email support'
            ],
            'professional': [
                'Process up to 2,000 PDFs/month',
                'Advanced PDF processing with OCR',
                'CareTend format conversion',
                'Processing history and analytics',
                'Phone and email support',
                'Custom branding'
            ],
            'enterprise': [
                'Unlimited PDF processing',
                'Advanced PDF processing with OCR',
                'CareTend format conversion',
                'Full analytics dashboard',
                'API access',
                'Custom branding',
                'Dedicated support',
                'SLA guarantee'
            ]
        }
        return features.get(plan, features['basic'])
    
    def _generate_setup_instructions(self, customer_data, login_url):
        """Generate setup instructions for customer"""
        return f"""
# {customer_data['pharmacy_name']} - PharmAssist Setup Instructions

## Welcome to PharmAssist Enterprise!

Your pharmacy's PDF processing system is now ready. Follow these steps to get started:

### 1. Access Your System
- **Login URL**: {login_url}
- **Admin Username**: {customer_data['admin_username']}
- **Temporary Password**: {customer_data['admin_password']}

⚠️ **Important**: Change your password immediately after first login!

### 2. System Features
Your {customer_data.get('plan', 'professional')} plan includes:
{chr(10).join(['• ' + feature for feature in self._get_plan_features(customer_data.get('plan'))])}

### 3. Getting Started
1. Login with your admin credentials
2. Change your password (required)
3. Upload your first PDF medication list
4. Review the CareTend format output
5. Add additional staff users if needed

### 4. Staff Training
- The system is designed for non-technical pharmacy staff
- Simply drag and drop PDF files to process them
- All processing is logged for compliance
- Results can be downloaded or emailed

### 5. Support
- Email: support@pharmassist.com
- Phone: 1-800-PHARMA-1
- Knowledge Base: Available in your dashboard

### 6. Security Notes
- All data is HIPAA compliant
- Processing history is logged for audit
- Sessions auto-expire for security
- SSL encryption throughout

## API Access (Enterprise plans)
Your API key: {customer_data.get('api_key', 'Contact support for API access')}

## Billing
Your subscription renews automatically. Contact billing@pharmassist.com for changes.

---
Thank you for choosing PharmAssist Enterprise!
"""

# Customer creation routes
def create_customer_routes(app, user_manager):
    """Add customer creation routes to Flask app"""
    
    @app.route('/admin/create-customer', methods=['GET', 'POST'])
    def create_customer():
        """Admin interface to create new customers"""
        if request.method == 'POST':
            customer_data = {
                'pharmacy_name': request.form['pharmacy_name'],
                'contact_email': request.form['contact_email'],
                'phone': request.form.get('phone'),
                'address': request.form.get('address'),
                'subdomain': request.form.get('subdomain'),
                'logo_url': request.form.get('logo_url'),
                'brand_color': request.form.get('brand_color', '#0078d4'),
                'plan': request.form.get('plan', 'professional'),
                'admin_username': request.form['admin_username'],
                'admin_email': request.form['admin_email'],
                'admin_password': request.form.get('admin_password') or secrets.token_urlsafe(12),
                'admin_first_name': request.form.get('admin_first_name'),
                'admin_last_name': request.form.get('admin_last_name')
            }
            
            onboarding = CustomerOnboarding(user_manager.connection)
            result = onboarding.generate_customer_package(customer_data)
            
            if result['status'] == 'success':
                return render_template('customer_package.html', package=result['package'])
            else:
                flash(f"Error creating customer: {result.get('error')}", 'error')
        
        return render_template('create_customer.html')
    
    @app.route('/login/<subdomain>')
    def branded_login(subdomain):
        """Branded login page for specific pharmacy"""
        tenant = user_manager.get_tenant_by_subdomain(subdomain)
        if not tenant:
            flash('Pharmacy not found', 'error')
            return redirect(url_for('generic_login'))
        
        return render_template('login_branded.html', tenant=tenant)
    
    @app.route('/api/validate-subdomain/<subdomain>')
    def validate_subdomain(subdomain):
        """API endpoint to check if subdomain is available"""
        tenant = user_manager.get_tenant_by_subdomain(subdomain)
        return jsonify({
            'available': tenant is None,
            'subdomain': subdomain
        })

# Usage example:
def setup_customer_onboarding(app, db_connection):
    """Setup customer onboarding system"""
    user_manager = UserManager(db_connection)
    create_customer_routes(app, user_manager)
    return user_manager
