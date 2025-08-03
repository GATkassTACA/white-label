"""
Debug WSGI entry point for troubleshooting deployment issues
"""
import os
import sys
from flask import Flask, jsonify

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

@app.route('/')
def debug_info():
    return f"""
    <h1>🔧 White Label Chat - Debug Info</h1>
    <h2>System Information</h2>
    <p><strong>Python Version:</strong> {sys.version}</p>
    <p><strong>Working Directory:</strong> {os.getcwd()}</p>
    <p><strong>Python Path:</strong> {sys.path}</p>
    
    <h2>Directory Contents</h2>
    <ul>
    {''.join(f'<li>{item}</li>' for item in os.listdir('.'))}
    </ul>
    
    <h2>Environment Variables</h2>
    <ul>
        <li>DATABASE_URL: {'✅ Configured' if os.environ.get('DATABASE_URL') else '❌ Missing'}</li>
        <li>REDIS_URL: {'✅ Configured' if os.environ.get('REDIS_URL') else '❌ Missing'}</li>
        <li>FLASK_ENV: {os.environ.get('FLASK_ENV', 'Not Set')}</li>
        <li>PORT: {os.environ.get('PORT', 'Not Set')}</li>
    </ul>
    
    <h2>Import Test</h2>
    <p><a href="/test-imports">Test Imports</a></p>
    """

@app.route('/test-imports')
def test_imports():
    results = []
    
    # Test basic imports
    try:
        import app
        results.append("✅ app module imported successfully")
    except Exception as e:
        results.append(f"❌ app module import failed: {e}")
    
    try:
        from app import create_app
        results.append("✅ create_app imported successfully")
    except Exception as e:
        results.append(f"❌ create_app import failed: {e}")
    
    try:
        import models
        results.append("✅ models module imported successfully")
    except Exception as e:
        results.append(f"❌ models module import failed: {e}")
    
    try:
        import config
        results.append("✅ config module imported successfully")
    except Exception as e:
        results.append(f"❌ config module import failed: {e}")
    
    return """
    <h1>🧪 Import Test Results</h1>
    <ul>
    """ + ''.join(f'<li>{result}</li>' for result in results) + """
    </ul>
    <p><a href="/">Back to Debug Info</a></p>
    """

@app.route('/health')
def health():
    return jsonify({"status": "ok", "message": "Debug app is running"})

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
