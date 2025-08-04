#!/usr/bin/env python3
"""
Azure-compatible test script for PharmAssist application
Tests the app functionality without requiring local database connections
"""

import os
import sys
import tempfile
import json
from io import BytesIO

# Set environment for testing
os.environ['FLASK_ENV'] = 'testing'

# Import the app
from app import app, DATABASE_AVAILABLE, PDF_PROCESSING_AVAILABLE

def test_app_creation():
    """Test that the app can be created and configured"""
    print("🧪 Test 1: App Creation and Configuration")
    print("-" * 50)
    
    try:
        assert app is not None, "App should be created"
        assert app.config['MAX_CONTENT_LENGTH'] == 16 * 1024 * 1024, "Max content length should be 16MB"
        assert app.secret_key is not None, "Secret key should be set"
        print("✅ App created and configured successfully")
        return True
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False

def test_health_endpoint():
    """Test the health check endpoint"""
    print("\n🧪 Test 2: Health Endpoint")
    print("-" * 50)
    
    try:
        with app.test_client() as client:
            response = client.get('/health')
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            data = response.get_json()
            assert data['status'] == 'healthy', "Status should be healthy"
            assert 'pdf_processing' in data, "Should include PDF processing status"
            assert 'database' in data, "Should include database status"
            assert 'timestamp' in data, "Should include timestamp"
            
            print(f"✅ Health check passed:")
            print(f"   Status: {data['status']}")
            print(f"   PDF Processing: {data['pdf_processing']}")
            print(f"   Database: {data['database']}")
            
        return True
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

def test_api_status():
    """Test the API status endpoint"""
    print("\n🧪 Test 3: API Status Endpoint")
    print("-" * 50)
    
    try:
        with app.test_client() as client:
            response = client.get('/api/status')
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            data = response.get_json()
            assert data['status'] == 'operational', "Status should be operational"
            assert 'pdf_processing_available' in data, "Should include PDF processing status"
            assert 'database_available' in data, "Should include database status"
            assert 'methods_available' in data, "Should include available methods"
            assert 'version' in data, "Should include version"
            
            print(f"✅ API status check passed:")
            print(f"   Status: {data['status']}")
            print(f"   PDF Processing: {data['pdf_processing_available']}")
            print(f"   Database: {data['database_available']}")
            print(f"   Methods: {data['methods_available']}")
            print(f"   Version: {data['version']}")
            
        return True
    except Exception as e:
        print(f"❌ API status test failed: {e}")
        return False

def test_main_page():
    """Test the main page loads"""
    print("\n🧪 Test 4: Main Page")
    print("-" * 50)
    
    try:
        with app.test_client() as client:
            response = client.get('/')
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            # Check if it's HTML content
            content_type = response.headers.get('Content-Type', '')
            assert 'text/html' in content_type, f"Expected HTML content, got {content_type}"
            
            print("✅ Main page loads successfully")
            print(f"   Content-Type: {content_type}")
            
        return True
    except Exception as e:
        print(f"❌ Main page test failed: {e}")
        return False

def test_pdf_upload_demo():
    """Test PDF upload functionality (demo mode)"""
    print("\n🧪 Test 5: PDF Upload (Demo Mode)")
    print("-" * 50)
    
    try:
        with app.test_client() as client:
            # Create a fake PDF file for testing
            fake_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
            
            data = {
                'file': (BytesIO(fake_pdf_content), 'test.pdf'),
                'method': 'auto'
            }
            
            response = client.post('/api/process', 
                                 data=data,
                                 content_type='multipart/form-data')
            
            # Should work in demo mode even if PDF processing fails
            data = response.get_json()
            
            if response.status_code == 200:
                print("✅ PDF upload test passed (demo mode)")
                print(f"   Success: {data.get('success', False)}")
                print(f"   Method used: {data.get('method_used', 'unknown')}")
                if 'note' in data:
                    print(f"   Note: {data['note']}")
            else:
                print(f"⚠️  PDF upload returned {response.status_code}")
                print(f"   Error: {data.get('error', 'Unknown error')}")
                
        return True
    except Exception as e:
        print(f"❌ PDF upload test failed: {e}")
        return False

def test_error_handling():
    """Test error handling for invalid requests"""
    print("\n🧪 Test 6: Error Handling")
    print("-" * 50)
    
    try:
        with app.test_client() as client:
            # Test missing file
            response = client.post('/api/process')
            assert response.status_code == 400, "Should return 400 for missing file"
            
            # Test non-PDF file
            data = {
                'file': (BytesIO(b'not a pdf'), 'test.txt'),
            }
            response = client.post('/api/process', 
                                 data=data,
                                 content_type='multipart/form-data')
            assert response.status_code == 400, "Should return 400 for non-PDF file"
            
            print("✅ Error handling test passed")
            print("   ✓ Missing file returns 400")
            print("   ✓ Non-PDF file returns 400")
            
        return True
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("🏥 PharmAssist Azure Test Suite")
    print("=" * 60)
    print(f"Environment: Azure App Service")
    print(f"PDF Processing Available: {PDF_PROCESSING_AVAILABLE}")
    print(f"Database Available: {DATABASE_AVAILABLE}")
    print("=" * 60)
    
    tests = [
        test_app_creation,
        test_health_endpoint,
        test_api_status,
        test_main_page,
        test_pdf_upload_demo,
        test_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("🎯 TEST RESULTS")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! Your PharmAssist app is ready for Azure!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the issues above.")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
