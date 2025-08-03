#!/usr/bin/env python3
"""
Test script for the authentication system
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_auth_endpoints():
    """Test authentication endpoints"""
    print("🔐 Testing Authentication System")
    print("=" * 50)
    
    # Test 1: Register new user
    print("\n📝 Test 1: User Registration")
    register_data = {
        "email": "test@example.com",
        "password": "Test123!",
        "username": "testuser",
        "full_name": "Test User",
        "client_id": "default"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        if response.status_code == 201:
            data = response.json()
            print("✅ Registration successful!")
            print(f"   User: {data['user']['username']}")
            print(f"   Email: {data['user']['email']}")
            print(f"   User Type: {data['user']['user_type']}")
            access_token = data['access_token']
        else:
            print(f"❌ Registration failed: {response.json()}")
            return
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return
    
    # Test 2: Login with existing user
    print("\n🔑 Test 2: User Login")
    login_data = {
        "email": "admin@example.com",
        "password": "Admin123!"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"   User: {data['user']['username']}")
            print(f"   User Type: {data['user']['user_type']}")
            admin_token = data['access_token']
        else:
            print(f"❌ Login failed: {response.json()}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Test 3: Protected route access
    print("\n🛡️ Test 3: Protected Route Access")
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Protected route access successful!")
            print(f"   Current user: {data['user']['username']}")
            print(f"   Email verified: {data['user']['email_verified']}")
        else:
            print(f"❌ Protected route failed: {response.json()}")
    except Exception as e:
        print(f"❌ Protected route error: {e}")
    
    # Test 4: Token verification
    print("\n🔍 Test 4: Token Verification")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/verify-token", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Token verification successful!")
            print(f"   Valid: {data['valid']}")
        else:
            print(f"❌ Token verification failed: {response.json()}")
    except Exception as e:
        print(f"❌ Token verification error: {e}")
    
    # Test 5: Invalid login
    print("\n❌ Test 5: Invalid Login")
    invalid_login = {
        "email": "invalid@example.com",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=invalid_login)
        if response.status_code == 401:
            print("✅ Invalid login correctly rejected!")
        else:
            print(f"❌ Invalid login not handled properly: {response.status_code}")
    except Exception as e:
        print(f"❌ Invalid login test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Authentication system tests completed!")

if __name__ == "__main__":
    test_auth_endpoints()
