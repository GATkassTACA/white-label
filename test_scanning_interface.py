"""
Test PharmAssist Main Interface and Processing UI
"""
import requests

BASE_URL = "https://pharmassist-enterprise.azurewebsites.net"

def test_main_interface():
    """Test the main PharmAssist interface"""
    print("🖥️ Testing PharmAssist Main Interface...")
    
    # Create session and login
    session = requests.Session()
    
    login_data = {
        'username': 'testpharmacist',
        'password': 'testpass123'
    }
    
    # Login
    response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
    if response.status_code in [302, 303]:
        print("✅ User login successful")
    else:
        print("❌ User login failed")
        return
    
    # Access main page
    response = session.get(f"{BASE_URL}/")
    if response.status_code == 200:
        print("✅ Main interface accessible")
        
        # Check for key UI elements
        content = response.text
        
        if "PharmAssist" in content:
            print("✅ PharmAssist branding present")
            
        if "upload" in content.lower() or "file" in content.lower():
            print("✅ File upload interface detected")
            
        if "pdf" in content.lower():
            print("✅ PDF processing references found")
            
        if "drag" in content.lower() or "drop" in content.lower():
            print("✅ Drag & drop interface likely present")
            
        # Look for processing methods
        methods = ['auto', 'pypdf2', 'pdfplumber', 'ocr']
        found_methods = []
        for method in methods:
            if method in content.lower():
                found_methods.append(method)
                
        if found_methods:
            print(f"✅ Processing methods available: {', '.join(found_methods)}")
        else:
            print("ℹ️ Processing method selection not visible in HTML")
            
        # Look for medication extraction features
        if "medication" in content.lower():
            print("✅ Medication extraction features referenced")
            
        if "download" in content.lower():
            print("✅ Download functionality referenced")
            
        # Show a snippet of the interface
        print("\n📄 Interface Preview (first 500 chars):")
        print("-" * 50)
        print(content[:500])
        print("-" * 50)
        
        # Look for JavaScript/frontend functionality
        if "<script" in content:
            print("✅ Interactive JavaScript functionality present")
            
        if "fetch" in content or "ajax" in content.lower():
            print("✅ AJAX/API integration detected")
            
    else:
        print(f"❌ Main interface not accessible: {response.status_code}")

def test_api_endpoints():
    """Test API endpoints directly"""
    print("\n🔌 Testing API Endpoints...")
    
    # Test public endpoints
    endpoints = [
        ('/health', 'Health Check'),
        ('/api/status', 'API Status'),
        ('/favicon.ico', 'Favicon')
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                print(f"✅ {name}: Working")
                if endpoint == '/health':
                    data = response.json()
                    print(f"   Database: {data.get('database', 'Unknown')}")
                    print(f"   PDF Processing: {data.get('pdf_processing', 'Unknown')}")
                elif endpoint == '/api/status':
                    data = response.json()
                    print(f"   Status: {data.get('status', 'Unknown')}")
                    print(f"   Methods: {data.get('methods_available', [])}")
            else:
                print(f"❌ {name}: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")

def test_processing_capabilities():
    """Test what processing capabilities are available"""
    print("\n⚙️ Testing Processing Capabilities...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        if response.status_code == 200:
            data = response.json()
            
            print(f"PDF Processing Available: {data.get('pdf_processing_available', False)}")
            print(f"Database Available: {data.get('database_available', False)}")
            print(f"System Status: {data.get('status', 'Unknown')}")
            print(f"Version: {data.get('version', 'Unknown')}")
            
            methods = data.get('methods_available', [])
            print(f"Available Processing Methods: {len(methods)}")
            for method in methods:
                print(f"  - {method}")
                
            if data.get('pdf_processing_available'):
                print("✅ System ready for PDF processing!")
            else:
                print("❌ PDF processing not available")
                
    except Exception as e:
        print(f"❌ Error checking capabilities: {e}")

def test_admin_processing_logs():
    """Check admin panel for processing insights"""
    print("\n📊 Testing Admin Processing Logs...")
    
    session = requests.Session()
    
    # Admin login
    login_data = {
        'username': 'pharmadmin',
        'password': 'admin'
    }
    
    response = session.post(f"{BASE_URL}/admin/auth", data=login_data, allow_redirects=False)
    if response.status_code in [302, 303]:
        print("✅ Admin login successful")
        
        # Check processing logs
        response = session.get(f"{BASE_URL}/admin/processing-logs")
        if response.status_code == 200:
            print("✅ Processing logs page accessible")
            
            content = response.text
            if "processing" in content.lower():
                print("✅ Processing log interface loaded")
            
            # Check API endpoint
            response = session.get(f"{BASE_URL}/admin/api/processing-logs")
            if response.status_code == 200:
                logs = response.json()
                print(f"✅ Processing logs API: {len(logs)} records")
                
                if logs:
                    print("Recent processing activity:")
                    for log in logs[:3]:
                        print(f"  - {log.get('filename', 'Unknown')} - {log.get('status', 'Unknown')}")
                else:
                    print("ℹ️ No processing history yet (system ready for first upload)")
            else:
                print("❌ Processing logs API not accessible")
        else:
            print("❌ Processing logs page not accessible")
    else:
        print("❌ Admin login failed")

def main():
    print("🧪 Testing PharmAssist Scanning Function & Interface")
    print("=" * 60)
    
    test_main_interface()
    test_api_endpoints()
    test_processing_capabilities()
    test_admin_processing_logs()
    
    print("\n" + "=" * 60)
    print("🏁 Interface and Scanning Function Testing Complete")
    
    print("\n💡 Next Steps for PDF Testing:")
    print("1. Upload a PDF through the web interface")
    print("2. Use browser developer tools to inspect AJAX calls")
    print("3. Check admin logs for processing results")
    print("4. Verify extracted text and medications")

if __name__ == "__main__":
    main()
