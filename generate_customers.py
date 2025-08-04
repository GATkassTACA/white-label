#!/usr/bin/env python3
"""
PharmAssist Customer Generator Script

This script helps you quickly generate customer accounts for PharmAssist.
Use this for rapid customer onboarding and credential generation.
"""

import secrets
import json
import datetime
from pathlib import Path

class PharmAssistCustomerGenerator:
    """Generate customer packages for PharmAssist"""
    
    def __init__(self):
        self.customers = []
    
    def generate_credentials(self, pharmacy_name, contact_email, 
                           subdomain=None, plan="professional", 
                           logo_url=None, brand_color="#0078d4"):
        """Generate customer credentials package"""
        
        # Generate secure credentials
        admin_username = pharmacy_name.lower().replace(' ', '').replace('&', '') + 'admin'
        admin_password = secrets.token_urlsafe(12)
        api_key = secrets.token_urlsafe(32)
        
        # Generate URLs
        base_url = "https://vitalcare.azurewebsites.net"
        if subdomain:
            login_url = f"{base_url}/login/{subdomain}"
        else:
            login_url = f"{base_url}/login?pharmacy={pharmacy_name.replace(' ', '+')}"
        
        # Calculate subscription expiry
        if plan == "trial":
            expires = datetime.datetime.now() + datetime.timedelta(days=30)
        elif plan == "monthly":
            expires = datetime.datetime.now() + datetime.timedelta(days=30)
        else:  # annual/professional/enterprise
            expires = datetime.datetime.now() + datetime.timedelta(days=365)
        
        # Plan features
        features = self._get_plan_features(plan)
        
        # Create customer package
        customer = {
            "pharmacy_info": {
                "name": pharmacy_name,
                "contact_email": contact_email,
                "subdomain": subdomain,
                "logo_url": logo_url,
                "brand_color": brand_color
            },
            "credentials": {
                "login_url": login_url,
                "admin_username": admin_username,
                "admin_password": admin_password,
                "api_key": api_key
            },
            "subscription": {
                "plan": plan,
                "expires": expires.isoformat(),
                "features": features
            },
            "setup_instructions": self._generate_instructions(pharmacy_name, login_url, admin_username, admin_password),
            "created_date": datetime.datetime.now().isoformat()
        }
        
        self.customers.append(customer)
        return customer
    
    def _get_plan_features(self, plan):
        """Get features for subscription plan"""
        features = {
            "trial": [
                "Process up to 100 PDFs/month",
                "Basic PDF processing",
                "Email support",
                "30-day trial period"
            ],
            "basic": [
                "Process up to 500 PDFs/month",
                "Standard PDF processing",
                "CareTend format conversion",
                "Email support"
            ],
            "professional": [
                "Process up to 2,000 PDFs/month",
                "Advanced PDF processing with OCR",
                "CareTend format conversion",
                "Processing history and analytics",
                "Phone and email support",
                "Custom branding"
            ],
            "enterprise": [
                "Unlimited PDF processing",
                "Advanced PDF processing with OCR",
                "CareTend format conversion",
                "Full analytics dashboard",
                "API access",
                "Custom branding",
                "Dedicated support",
                "SLA guarantee"
            ]
        }
        return features.get(plan, features["basic"])
    
    def _generate_instructions(self, pharmacy_name, login_url, username, password):
        """Generate setup instructions"""
        return f"""
# {pharmacy_name} - PharmAssist Setup Instructions

## Welcome to PharmAssist Enterprise!

### Quick Start:
1. Visit: {login_url}
2. Username: {username}
3. Password: {password}
4. **IMPORTANT**: Change password on first login!

### First Steps:
1. Login with provided credentials
2. Change your password (required)
3. Upload a test PDF medication list
4. Review the CareTend format output
5. Add staff users as needed

### Support:
- Email: support@pharmassist.com
- Phone: 1-800-PHARMA-1
- Knowledge Base: Available in dashboard

### Security:
- HIPAA compliant processing
- All sessions are encrypted
- Audit logs maintained
- Auto-logout for security

Thank you for choosing PharmAssist Enterprise!
"""
    
    def save_customer_package(self, customer, output_dir="customer_packages"):
        """Save customer package to file"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        pharmacy_name = customer["pharmacy_info"]["name"]
        safe_name = "".join(c for c in pharmacy_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_name.replace(' ', '_')}_pharmassist_package.json"
        
        filepath = output_path / filename
        
        with open(filepath, 'w') as f:
            json.dump(customer, f, indent=2)
        
        return filepath
    
    def generate_multiple_customers(self, customers_data):
        """Generate multiple customer packages"""
        packages = []
        
        for customer_data in customers_data:
            package = self.generate_credentials(**customer_data)
            filepath = self.save_customer_package(package)
            packages.append({
                "package": package,
                "filepath": filepath
            })
        
        return packages
    
    def export_summary_csv(self, filename="customer_summary.csv"):
        """Export customer summary as CSV"""
        import csv
        
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = [
                'pharmacy_name', 'contact_email', 'login_url', 
                'admin_username', 'plan', 'created_date'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for customer in self.customers:
                writer.writerow({
                    'pharmacy_name': customer['pharmacy_info']['name'],
                    'contact_email': customer['pharmacy_info']['contact_email'],
                    'login_url': customer['credentials']['login_url'],
                    'admin_username': customer['credentials']['admin_username'],
                    'plan': customer['subscription']['plan'],
                    'created_date': customer['created_date']
                })

# Example usage
if __name__ == "__main__":
    # Initialize generator
    generator = PharmAssistCustomerGenerator()
    
    # Example customers
    example_customers = [
        {
            "pharmacy_name": "Sunshine Pharmacy",
            "contact_email": "manager@sunshinepharmacy.com",
            "subdomain": "sunshine",
            "plan": "professional",
            "brand_color": "#f59e0b"
        },
        {
            "pharmacy_name": "City Center Drugs",
            "contact_email": "admin@citycenter.com",
            "subdomain": "citycenter",
            "plan": "enterprise",
            "brand_color": "#dc2626"
        },
        {
            "pharmacy_name": "Wellness Pharmacy Group",
            "contact_email": "it@wellnessgroup.com",
            "plan": "trial",
            "brand_color": "#059669"
        }
    ]
    
    # Generate packages
    print("🏥 PharmAssist Customer Generator")
    print("=" * 40)
    
    packages = generator.generate_multiple_customers(example_customers)
    
    for i, package_info in enumerate(packages, 1):
        customer = package_info["package"]
        filepath = package_info["filepath"]
        
        print(f"\n✅ Customer {i}: {customer['pharmacy_info']['name']}")
        print(f"   Login URL: {customer['credentials']['login_url']}")
        print(f"   Username: {customer['credentials']['admin_username']}")
        print(f"   Password: {customer['credentials']['admin_password']}")
        print(f"   Plan: {customer['subscription']['plan']}")
        print(f"   Package saved: {filepath}")
    
    # Export summary
    generator.export_summary_csv()
    print(f"\n📊 Summary exported to: customer_summary.csv")
    print(f"📁 {len(packages)} customer packages created in 'customer_packages/' directory")
    
    print("\n🎉 Customer generation complete!")
    print("Each pharmacy can now access their branded PharmAssist portal.")
