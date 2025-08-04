#!/usr/bin/env python3
"""
Azure App Service Health Check Script
Quick health verification for PharmAssist in Azure environment
"""

import requests
import json
import os
import sys
from datetime import datetime

def check_app_health(base_url="http://localhost"):
    """Check the health of the PharmAssist application"""
    
    print("🔍 Azure App Service Health Check")
    print("=" * 50)
    print(f"Target URL: {base_url}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    checks = []
    
    # 1. Health endpoint check
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            checks.append({
                'name': 'Health Endpoint',
                'status': '✅ PASS',
                'details': f"Status: {data.get('status', 'unknown')}"
            })
        else:
            checks.append({
                'name': 'Health Endpoint',
                'status': '❌ FAIL',
                'details': f"HTTP {response.status_code}"
            })
    except Exception as e:
        checks.append({
            'name': 'Health Endpoint',
            'status': '❌ FAIL',
            'details': f"Error: {str(e)}"
        })
    
    # 2. API Status check
    try:
        response = requests.get(f"{base_url}/api/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            checks.append({
                'name': 'API Status',
                'status': '✅ PASS',
                'details': f"PDF: {data.get('pdf_processing_available')}, DB: {data.get('database_available')}"
            })
        else:
            checks.append({
                'name': 'API Status',
                'status': '❌ FAIL',
                'details': f"HTTP {response.status_code}"
            })
    except Exception as e:
        checks.append({
            'name': 'API Status',
            'status': '❌ FAIL',
            'details': f"Error: {str(e)}"
        })
    
    # 3. Main page check
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            checks.append({
                'name': 'Main Page',
                'status': '✅ PASS',
                'details': f"Content length: {len(response.content)} bytes"
            })
        else:
            checks.append({
                'name': 'Main Page',
                'status': '❌ FAIL',
                'details': f"HTTP {response.status_code}"
            })
    except Exception as e:
        checks.append({
            'name': 'Main Page',
            'status': '❌ FAIL',
            'details': f"Error: {str(e)}"
        })
    
    # Print results
    for check in checks:
        print(f"{check['status']} {check['name']}")
        print(f"   {check['details']}")
    
    # Summary
    passed = sum(1 for check in checks if '✅' in check['status'])
    total = len(checks)
    
    print("-" * 50)
    print(f"Summary: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All health checks passed!")
        return True
    else:
        print("⚠️  Some health checks failed")
        return False

def check_azure_environment():
    """Check Azure-specific environment variables"""
    print("\n🌐 Azure Environment Check")
    print("-" * 50)
    
    azure_vars = [
        'WEBSITE_SITE_NAME',
        'WEBSITE_RESOURCE_GROUP', 
        'WEBSITE_HOSTNAME',
        'DATABASE_URL',
        'PORT'
    ]
    
    found_vars = []
    for var in azure_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive information
            if 'DATABASE' in var or 'PASSWORD' in var:
                display_value = f"{value[:10]}..." if len(value) > 10 else "***"
            else:
                display_value = value
            found_vars.append(f"✅ {var}: {display_value}")
        else:
            found_vars.append(f"❌ {var}: Not set")
    
    for var_info in found_vars:
        print(f"   {var_info}")
    
    return len([v for v in found_vars if '✅' in v])

if __name__ == '__main__':
    # Check if we're running in Azure by looking for Azure-specific env vars
    is_azure = bool(os.getenv('WEBSITE_SITE_NAME'))
    
    if is_azure:
        print("🌐 Detected Azure App Service environment")
        base_url = f"https://{os.getenv('WEBSITE_HOSTNAME', 'localhost')}"
    else:
        print("🖥️  Running in local/development environment")
        port = os.getenv('PORT', '5000')
        base_url = f"http://localhost:{port}"
    
    # Run environment check
    env_vars_found = check_azure_environment()
    
    # Run health checks
    if len(sys.argv) > 1 and sys.argv[1] == '--health-only':
        health_ok = check_app_health(base_url)
        sys.exit(0 if health_ok else 1)
    else:
        print(f"\n💡 To run health checks against the running app, use:")
        print(f"   python azure_health_check.py --health-only")
        print(f"\n🔗 App should be available at: {base_url}")
