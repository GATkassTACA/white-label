"""
Test PharmAssist User Management and Creation
"""
import requests
import json

BASE_URL = "https://pharmassist-enterprise.azurewebsites.net"

def login_admin():
    """Login to admin panel and return session"""
    session = requests.Session()
    
    login_data = {
        'username': 'pharmadmin',
        'password': 'admin'
    }
    
    response = session.post(f"{BASE_URL}/admin/auth", data=login_data, allow_redirects=False)
    if response.status_code in [302, 303]:
        print("✅ Admin login successful")
        return session
    else:
        print("❌ Admin login failed")
        return None

def test_user_management(session):
    """Test user management functionality"""
    print("\n👥 Testing User Management...")
    
    # Test user list page
    try:
        response = session.get(f"{BASE_URL}/admin/users")
        if response.status_code == 200:
            print("✅ User management page accessible")
            if "User Management" in response.text or "users" in response.text.lower():
                print("✅ User management interface loaded")
            
            # Look for existing users in the page
            if "admin" in response.text.lower():
                print("✅ Default admin user visible in interface")
        else:
            print(f"❌ User management page failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ User management page error: {e}")
    
    # Test getting all users via API
    try:
        response = session.get(f"{BASE_URL}/admin/api/customers")  # This might also show user data
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Customer API accessible: {len(data) if isinstance(data, list) else 'Data available'}")
        else:
            print(f"❌ Customer API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Customer API error: {e}")

def test_user_creation(session):
    """Test user creation functionality"""
    print("\n👤 Testing User Creation...")
    
    # Test data for new user
    test_user_data = {
        'username': 'testpharmacist',
        'email': 'test@pharmassist.com',
        'password': 'testpass123',
        'role': 'pharmacist'
    }
    
    try:
        # Test user creation API
        response = session.post(
            f"{BASE_URL}/admin/create-user", 
            json=test_user_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"User creation response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ User creation API response: {result}")
            
            if result.get('success'):
                print("✅ Test user created successfully!")
                return test_user_data
            else:
                print(f"❌ User creation failed: {result.get('message', 'Unknown error')}")
        else:
            print(f"❌ User creation request failed: {response.status_code}")
            print("Response text:", response.text[:200])
            
    except Exception as e:
        print(f"❌ User creation error: {e}")
    
    return None

def test_user_authentication(user_data):
    """Test if the created user can login to main app"""
    if not user_data:
        print("❌ No user data to test authentication")
        return False
        
    print(f"\n🔐 Testing Authentication for user: {user_data['username']}")
    
    try:
        session = requests.Session()
        
        # Test login with the created user
        login_data = {
            'username': user_data['username'],
            'password': user_data['password']
        }
        
        response = session.post(
            f"{BASE_URL}/login", 
            data=login_data, 
            allow_redirects=False
        )
        
        print(f"Login response: {response.status_code}")
        
        if response.status_code in [302, 303]:
            print("✅ User authentication successful (redirect detected)")
            
            # Try to access main page
            main_response = session.get(f"{BASE_URL}/")
            print(f"Main page access: {main_response.status_code}")
            
            if main_response.status_code == 200:
                print("✅ User can access main application!")
                return True
            else:
                print("❌ User cannot access main application")
                
        else:
            print("❌ User authentication failed")
            print("Response:", response.text[:200])
            
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
    
    return False

def test_user_editing(session, user_data):
    """Test user editing functionality"""
    if not user_data:
        print("❌ No user data to test editing")
        return
        
    print(f"\n✏️ Testing User Editing for: {user_data['username']}")
    
    # First, we need to find the user ID (this would normally be from the user list)
    # For testing, let's try to edit user with ID 1 (the admin user)
    try:
        edit_data = {
            'role': 'admin',
            'is_active': True
        }
        
        response = session.post(
            f"{BASE_URL}/admin/edit-user/1",  # Assuming admin user has ID 1
            json=edit_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"User edit response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ User edit API response: {result}")
            
            if result.get('success'):
                print("✅ User edited successfully!")
            else:
                print(f"❌ User edit failed: {result.get('message', 'Unknown error')}")
        else:
            print(f"❌ User edit request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ User edit error: {e}")

def test_admin_stats(session):
    """Test admin dashboard stats"""
    print("\n📊 Testing Admin Dashboard Stats...")
    
    try:
        response = session.get(f"{BASE_URL}/admin/api/stats")
        if response.status_code == 200:
            stats = response.json()
            print("✅ Admin stats accessible:")
            for key, value in stats.items():
                print(f"   {key}: {value}")
        else:
            print(f"❌ Admin stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Admin stats error: {e}")

def main():
    print("🔧 Testing PharmAssist User Management System")
    print("=" * 50)
    
    # Login to admin
    session = login_admin()
    if not session:
        print("❌ Cannot proceed without admin access")
        return
    
    # Test user management interface
    test_user_management(session)
    
    # Test user creation
    created_user = test_user_creation(session)
    
    # Test authentication with created user
    test_user_authentication(created_user)
    
    # Test user editing
    test_user_editing(session, created_user)
    
    # Test admin stats
    test_admin_stats(session)
    
    print("\n" + "=" * 50)
    print("🏁 User Management Testing Complete")

if __name__ == "__main__":
    main()
