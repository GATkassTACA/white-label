"""
Test PharmAssist PDF Scanning/Processing Functionality
"""
import requests
import json
import os
import time

BASE_URL = "https://pharmassist-enterprise.azurewebsites.net"

def login_user():
    """Login with our test user and return session"""
    session = requests.Session()
    
    login_data = {
        'username': 'testpharmacist',
        'password': 'testpass123'
    }
    
    response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
    if response.status_code in [302, 303]:
        print("✅ User login successful")
        return session
    else:
        print("❌ User login failed")
        return None

def create_test_pdf():
    """Create a simple test PDF for processing"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        filename = "test_prescription.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        
        # Add prescription-like content
        c.drawString(100, 750, "PHARMACY PRESCRIPTION")
        c.drawString(100, 730, "Patient: John Doe")
        c.drawString(100, 710, "DOB: 01/15/1980")
        c.drawString(100, 690, "Address: 123 Main St, City, State 12345")
        c.drawString(100, 650, "Rx Number: 1234567")
        c.drawString(100, 630, "Date: 08/04/2025")
        c.drawString(100, 590, "MEDICATIONS:")
        c.drawString(120, 570, "1. Lisinopril 10mg - Take 1 tablet daily")
        c.drawString(120, 550, "2. Metformin 500mg - Take 2 tablets twice daily")
        c.drawString(120, 530, "3. Atorvastatin 20mg - Take 1 tablet at bedtime")
        c.drawString(100, 490, "Doctor: Dr. Jane Smith")
        c.drawString(100, 470, "DEA: AS1234567")
        c.drawString(100, 430, "Pharmacy: PharmAssist Test Pharmacy")
        c.drawString(100, 410, "Phone: (555) 123-4567")
        
        c.save()
        print(f"✅ Created test PDF: {filename}")
        return filename
        
    except ImportError:
        print("❌ reportlab not available, will use alternate test method")
        return None
    except Exception as e:
        print(f"❌ Error creating test PDF: {e}")
        return None

def create_simple_text_file():
    """Create a simple text file that we can test with"""
    filename = "test_prescription.txt"
    content = """PHARMACY PRESCRIPTION
Patient: John Doe
DOB: 01/15/1980
Address: 123 Main St, City, State 12345

Rx Number: 1234567
Date: 08/04/2025

MEDICATIONS:
1. Lisinopril 10mg - Take 1 tablet daily
2. Metformin 500mg - Take 2 tablets twice daily  
3. Atorvastatin 20mg - Take 1 tablet at bedtime

Doctor: Dr. Jane Smith
DEA: AS1234567

Pharmacy: PharmAssist Test Pharmacy
Phone: (555) 123-4567
"""
    
    with open(filename, 'w') as f:
        f.write(content)
    
    print(f"✅ Created test text file: {filename}")
    return filename

def test_processing_methods(session):
    """Test different PDF processing methods"""
    print("\n🔬 Testing PDF Processing Methods...")
    
    methods = ['auto', 'pypdf2', 'pdfplumber', 'ocr']
    
    for method in methods:
        try:
            # Test each method with a simple API call
            test_data = {
                'method': method,
                'test': True
            }
            
            response = session.post(
                f"{BASE_URL}/api/process",
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Method '{method}' - Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {method}: {result}")
            else:
                print(f"❌ {method}: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ {method} error: {e}")

def test_file_upload_processing(session, test_file):
    """Test actual file upload and processing"""
    if not test_file or not os.path.exists(test_file):
        print("❌ No test file available for upload testing")
        return
        
    print(f"\n📁 Testing File Upload Processing with: {test_file}")
    
    try:
        # Test file upload processing
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'application/pdf')}
            data = {
                'method': 'auto',
                'extract_medications': 'true'
            }
            
            response = session.post(
                f"{BASE_URL}/api/process",
                files=files,
                data=data
            )
            
            print(f"File upload response: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ File processing successful!")
                print(f"Processing result: {json.dumps(result, indent=2)}")
                
                # Check for expected fields
                if 'medications' in result:
                    print(f"✅ Medications extracted: {len(result['medications'])} found")
                    for med in result['medications'][:3]:  # Show first 3
                        print(f"   - {med}")
                        
                if 'text' in result:
                    print(f"✅ Text extracted: {len(result['text'])} characters")
                    
                if 'processing_time' in result:
                    print(f"✅ Processing time: {result['processing_time']} seconds")
                    
            else:
                print(f"❌ File processing failed: {response.status_code}")
                print("Response:", response.text[:200])
                
    except Exception as e:
        print(f"❌ File upload error: {e}")

def test_medication_extraction():
    """Test medication extraction with sample text"""
    print("\n💊 Testing Medication Extraction...")
    
    sample_texts = [
        "Take Lisinopril 10mg once daily for blood pressure",
        "Metformin 500mg twice daily with meals",
        "Atorvastatin 20mg at bedtime for cholesterol",
        "Ibuprofen 400mg as needed for pain, maximum 3 times daily",
        "Amoxicillin 875mg twice daily for 10 days"
    ]
    
    session = requests.Session()
    
    for text in sample_texts:
        try:
            test_data = {
                'text': text,
                'extract_medications': True
            }
            
            response = session.post(
                f"{BASE_URL}/api/process",
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                medications = result.get('medications', [])
                print(f"✅ Text: '{text[:50]}...'")
                print(f"   Extracted: {medications}")
            else:
                print(f"❌ Failed to process: '{text[:30]}...'")
                
        except Exception as e:
            print(f"❌ Medication extraction error: {e}")

def test_processing_history(session):
    """Test processing history tracking"""
    print("\n📊 Testing Processing History...")
    
    try:
        # Check if there's an endpoint to view processing history
        response = session.get(f"{BASE_URL}/api/history")
        
        if response.status_code == 200:
            history = response.json()
            print(f"✅ Processing history accessible: {len(history)} records")
            
            for record in history[:3]:  # Show first 3 records
                print(f"   - {record.get('filename', 'Unknown')} - {record.get('status', 'Unknown')}")
                
        elif response.status_code == 404:
            print("ℹ️ Processing history endpoint not available")
        else:
            print(f"❌ Processing history failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Processing history error: {e}")

def test_download_functionality(session):
    """Test processed file download"""
    print("\n⬇️ Testing Download Functionality...")
    
    try:
        # Test download endpoint
        download_data = {
            'session_id': 'test-session',
            'format': 'txt'
        }
        
        response = session.post(
            f"{BASE_URL}/api/download",
            json=download_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Download test response: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Download functionality working")
            if response.headers.get('content-type'):
                print(f"   Content-Type: {response.headers['content-type']}")
        else:
            print(f"❌ Download test failed: {response.text[:100]}")
            
    except Exception as e:
        print(f"❌ Download test error: {e}")

def main():
    print("🔬 Testing PharmAssist PDF Scanning & Processing")
    print("=" * 55)
    
    # Login user
    session = login_user()
    if not session:
        print("❌ Cannot proceed without user access")
        return
    
    # Test processing methods availability
    test_processing_methods(session)
    
    # Create test file and test upload processing
    test_file = create_test_pdf()
    if not test_file:
        test_file = create_simple_text_file()
    
    test_file_upload_processing(session, test_file)
    
    # Test medication extraction
    test_medication_extraction()
    
    # Test processing history
    test_processing_history(session)
    
    # Test download functionality
    test_download_functionality(session)
    
    # Cleanup
    if test_file and os.path.exists(test_file):
        try:
            os.remove(test_file)
            print(f"🧹 Cleaned up test file: {test_file}")
        except:
            pass
    
    print("\n" + "=" * 55)
    print("🏁 PDF Processing Testing Complete")

if __name__ == "__main__":
    main()
