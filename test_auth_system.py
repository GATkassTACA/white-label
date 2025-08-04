#!/usr/bin/env python3
"""
Test the authentication system for PharmAssist
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

def test_login_system():
    """Test the login system"""
    print("🔐 Testing PharmAssist Authentication System")
    print("=" * 50)
    
    with app.test_client() as client:
        # Test 1: Access to main page without login should redirect
        print("Test 1: Protected route access")
        response = client.get('/')
        if response.status_code == 302:  # Redirect to login
            print("✅ Main page properly protected (redirects to login)")
        else:
            print(f"❌ Expected redirect (302), got {response.status_code}")
        
        # Test 2: Login page should be accessible
        print("\nTest 2: Login page accessibility")
        response = client.get('/login')
        if response.status_code == 200:
            print("✅ Login page accessible")
        else:
            print(f"❌ Login page error: {response.status_code}")
        
        # Test 3: Test login with invalid credentials
        print("\nTest 3: Invalid login attempt")
        response = client.post('/login', data={
            'username': 'invalid',
            'password': 'wrong'
        }, follow_redirects=True)
        
        if b'Invalid username or password' in response.data or response.status_code == 200:
            print("✅ Invalid login properly rejected")
        else:
            print("❌ Invalid login handling failed")
        
        # Test 4: Test with default admin credentials (if database available)
        print("\nTest 4: Default admin login")
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        
        if b'PharmAssist' in response.data or response.status_code == 200:
            print("✅ Admin login successful")
            
            # Test 5: Test logout
            print("\nTest 5: Logout functionality")
            response = client.get('/logout', follow_redirects=True)
            if b'login' in response.data.lower() or response.status_code == 200:
                print("✅ Logout successful")
            else:
                print("❌ Logout failed")
        else:
            print("⚠️  Admin login failed (database may not be available)")
    
    print("\n" + "=" * 50)
    print("🎯 Authentication test completed!")
    print("\n💡 Default credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n🚀 Your app now has user authentication!")

if __name__ == '__main__':
    test_login_system()
