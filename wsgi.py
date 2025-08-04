"""
WSGI entry point for production deployment of PharmAssist application
"""
import os
import sys
import traceback
from flask import Flask, jsonify

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Starting PharmAssist Application...")
print(f"Python path: {sys.path}")
print(f"Current working directory: {os.getcwd()}")
print(f"Directory contents: {os.listdir('.')}")

# Set production environment
os.environ['FLASK_ENV'] = 'production'

# Set basic configuration for Azure
os.environ.setdefault('SECRET_KEY', 'pharmassist-secure-key-2025')

# Set database URL if not already configured (for PostgreSQL)
if not os.environ.get('DATABASE_URL'):
    # Azure PostgreSQL connection format
    database_host = os.environ.get('DATABASE_HOST', 'localhost')
    database_name = os.environ.get('DATABASE_NAME', 'pharmassist_db')
    database_user = os.environ.get('DATABASE_USER', 'pharmadmin')
    database_password = os.environ.get('DATABASE_PASSWORD', '')
    
    if database_host and database_name and database_user and database_password:
        os.environ['DATABASE_URL'] = f'postgresql://{database_user}:{database_password}@{database_host}:5432/{database_name}?sslmode=require'
        print("Set DATABASE_URL from individual environment variables")

print(f"DATABASE_URL configured: {bool(os.environ.get('DATABASE_URL'))}")

try:
    print("Attempting to import app from the app module...")
    
    # Test individual imports first
    print("Testing flask import...")
    import flask
    print(f"Flask version: {flask.__version__}")
    
    print("Testing minimal test_app module import...")
    from test_app import app
    print("Successfully imported app from test_app")
    
    print("PharmAssist WSGI app loaded successfully!")
    print(f"Flask app: {app}")
    print(f"Environment: {os.environ.get('FLASK_ENV')}")
    
except Exception as e:
    print(f"Error loading PharmAssist app: {e}")
    traceback.print_exc()
    
    # Create a fallback Flask app with detailed error info
    print("Creating fallback Flask app...")
    app = Flask(__name__)
    
    @app.route('/')
    def hello():
        return f"""
        <h1>🏥 PharmAssist - Loading Error</h1>
        <p><strong>Error:</strong> {str(e)}</p>
        <p><strong>Python Path:</strong> {sys.path}</p>
        <p><strong>Working Directory:</strong> {os.getcwd()}</p>
        <p><strong>Directory Contents:</strong> {os.listdir('.')}</p>
        <p><strong>Environment Variables:</strong></p>
        <ul>
            <li>DATABASE_URL: {'✅ Configured' if os.environ.get('DATABASE_URL') else '❌ Missing'}</li>
            <li>SECRET_KEY: {'✅ Configured' if os.environ.get('SECRET_KEY') else '❌ Missing'}</li>
            <li>FLASK_ENV: {os.environ.get('FLASK_ENV', 'Not Set')}</li>
        </ul>
        <p><a href="/health">Health Check</a></p>
        """
    
    @app.route('/health')
    def health():
        return jsonify({
            "status": "error", 
            "message": str(e), 
            "python_path": sys.path, 
            "cwd": os.getcwd(),
            "environment": {
                "DATABASE_URL": bool(os.environ.get('DATABASE_URL')),
                "SECRET_KEY": bool(os.environ.get('SECRET_KEY')),
                "FLASK_ENV": os.environ.get('FLASK_ENV')
            }
        })

# For Azure App Service, we expose the app directly
# The Gunicorn server will handle the WSGI interface
if __name__ == "__main__":
    print("Starting in development mode...")
    port = int(os.environ.get('PORT', 8000))
    print(f"Using port: {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
