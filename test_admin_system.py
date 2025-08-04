#!/usr/bin/env python3
"""
Test the admin dashboard user management functionality
"""

import os
import sys
import importlib.util

# Set testing environment
os.environ['FLASK_ENV'] = 'testing'

# Import the app
spec = importlib.util.spec_from_file_location("app_module", "app.py")
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)

app = app_module.app

def test_admin_routes():
    """Test admin routes are available"""
    print("🔧 Testing Admin Dashboard Routes")
    print("=" * 50)
    
    with app.test_client() as client:
        # Test admin login page
        print("Test 1: Admin login page")
        response = client.get('/admin')
        if response.status_code == 200:
            print("✅ Admin login page accessible")
        else:
            print(f"❌ Admin login failed: {response.status_code}")
        
        # Test admin authentication
        print("\nTest 2: Admin authentication")
        response = client.post('/admin/auth', data={
            'username': 'pharmadmin',
            'password': 'admin'
        }, follow_redirects=False)
        
        if response.status_code == 302:  # Redirect after successful login
            print("✅ Admin authentication working")
            
            # Test dashboard access after login
            print("\nTest 3: Dashboard access")
            
            # Simulate logged in session
            with client.session_transaction() as sess:
                sess['admin_logged_in'] = True
                sess['admin_user'] = 'pharmadmin'
            
            # Test dashboard
            response = client.get('/admin/dashboard')
            if response.status_code == 200:
                print("✅ Admin dashboard accessible")
            else:
                print(f"❌ Dashboard access failed: {response.status_code}")
            
            # Test users page
            response = client.get('/admin/users')
            if response.status_code == 200:
                print("✅ Users management page accessible")
            else:
                print(f"❌ Users page failed: {response.status_code}")
                
        else:
            print(f"❌ Admin authentication failed: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎯 Admin routes test completed!")

if __name__ == '__main__':
    test_admin_routes()
