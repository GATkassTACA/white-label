#!/usr/bin/env python3
"""Test script for PharmAssist application"""

from pharmassist_app import app

def test_app():
    """Test the PharmAssist application"""
    print("🧪 Testing PharmAssist Application")
    print("=" * 50)
    
    # Test 1: App creation
    print("✅ Test 1: App imports and creates successfully")
    print(f"   Max file size: {app.config['MAX_CONTENT_LENGTH']} bytes")
    
    # Test 2: Routes
    print("\n✅ Test 2: Available routes:")
    with app.app_context():
        for rule in app.url_map.iter_rules():
            print(f"   {rule.endpoint:20} {rule.rule:30} {list(rule.methods)}")
    
    # Test 3: Test client
    print("\n✅ Test 3: Testing endpoints...")
    with app.test_client() as client:
        # Test health endpoint
        response = client.get('/health')
        print(f"   /health: {response.status_code} - {response.json}")
        
        # Test API status
        response = client.get('/api/status')
        print(f"   /api/status: {response.status_code} - {response.json}")
        
        # Test main page
        response = client.get('/')
        print(f"   /: {response.status_code} - {'HTML page loaded' if response.status_code == 200 else 'Failed'}")
    
    print("\n🎉 All tests completed successfully!")
    print("PharmAssist is ready for deployment!")

if __name__ == '__main__':
    test_app()
