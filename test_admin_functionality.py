"""
Quick test script to verify PharmAssist admin functionality
"""
import requests

BASE_URL = "https://pharmassist-enterprise.azurewebsites.net"

def test_endpoints():
    print("🧪 Testing PharmAssist Endpoints...")
    
    # Test health
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health endpoint:", response.json())
        else:
            print("❌ Health endpoint failed:", response.status_code)
    except Exception as e:
        print("❌ Health endpoint error:", e)
    
    # Test API status
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        if response.status_code == 200:
            print("✅ API Status:", response.json())
        else:
            print("❌ API Status failed:", response.status_code)
    except Exception as e:
        print("❌ API Status error:", e)
    
    # Test admin login page
    try:
        response = requests.get(f"{BASE_URL}/admin")
        if response.status_code == 200:
            print("✅ Admin login page loads successfully")
            if "Admin Login" in response.text:
                print("✅ Admin login form found")
            else:
                print("❌ Admin login form not found")
        else:
            print("❌ Admin login page failed:", response.status_code)
    except Exception as e:
        print("❌ Admin login page error:", e)
    
    # Test main login page
    try:
        response = requests.get(f"{BASE_URL}/login")
        if response.status_code == 200:
            print("✅ Main login page loads successfully")
            if "PharmAssist" in response.text:
                print("✅ PharmAssist branding found")
            else:
                print("❌ PharmAssist branding not found")
        else:
            print("❌ Main login page failed:", response.status_code)
    except Exception as e:
        print("❌ Main login page error:", e)

def test_admin_auth():
    print("\n🔐 Testing Admin Authentication...")
    
    session = requests.Session()
    
    # Test admin authentication
    try:
        login_data = {
            'username': 'pharmadmin',
            'password': 'admin'
        }
        
        response = session.post(f"{BASE_URL}/admin/auth", data=login_data, allow_redirects=False)
        print(f"Admin auth response: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code in [302, 303]:  # Redirect indicates success
            print("✅ Admin authentication appears successful (redirect)")
            
            # Try to access dashboard
            dashboard_response = session.get(f"{BASE_URL}/admin/dashboard")
            print(f"Dashboard access: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("✅ Admin dashboard accessible!")
                if "Dashboard" in dashboard_response.text:
                    print("✅ Dashboard content loaded")
            else:
                print("❌ Dashboard not accessible")
                
        else:
            print("❌ Admin authentication failed")
            print("Response text:", response.text[:200])
            
    except Exception as e:
        print("❌ Admin authentication error:", e)

if __name__ == "__main__":
    test_endpoints()
    test_admin_auth()
