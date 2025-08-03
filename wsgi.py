"""
WSGI entry point for production deployment
"""
import os
import sys
import traceback
from flask import Flask, jsonify

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Starting WSGI application...")
print(f"Python path: {sys.path}")
print(f"Current working directory: {os.getcwd()}")
print(f"Directory contents: {os.listdir('.')}")

# Set production environment
os.environ['FLASK_ENV'] = 'production'

# Set basic configuration for Azure
os.environ.setdefault('SECRET_KEY', 'azure-production-secret-key-change-me')
os.environ.setdefault('JWT_SECRET_KEY', 'azure-jwt-secret-key-change-me')

# Set database URL if not already configured
if not os.environ.get('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'postgresql://dbadmin:Unicorn1982@white-label-db-km.postgres.database.azure.com:5432/postgres?sslmode=require'
    print("Set fallback DATABASE_URL")

print(f"DATABASE_URL configured: {bool(os.environ.get('DATABASE_URL'))}")

try:
    print("Attempting to import create_app...")
    from app import create_app
    print("Successfully imported create_app")
    
    # Create the Flask app and SocketIO instance
    print("Creating Flask application...")
    flask_app, socketio = create_app()
    
    # For Azure App Service, expose the Flask app directly
    # Note: SocketIO functionality may be limited in this deployment mode
    app = flask_app
    
    print("WSGI app created successfully")
    print(f"Flask app: {app}")
    print(f"Environment: {os.environ.get('FLASK_ENV')}")
    
except Exception as e:
    print(f"Error creating WSGI app: {e}")
    traceback.print_exc()
    
    # Create a minimal Flask app as fallback
    print("Creating fallback Flask app...")
    app = Flask(__name__)
    
    @app.route('/')
    def hello():
        return f"""
        <h1>🚨 WSGI Loading Error</h1>
        <p><strong>Error:</strong> {str(e)}</p>
        <p><strong>Python Path:</strong> {sys.path}</p>
        <p><strong>Working Directory:</strong> {os.getcwd()}</p>
        <p><strong>Directory Contents:</strong> {os.listdir('.')}</p>
        <p><a href="/api/health">Health Check</a></p>
        """
    
    @app.route('/api/health')
    def health():
        return jsonify({"status": "error", "message": str(e), "python_path": sys.path, "cwd": os.getcwd()})

# For Azure App Service, we expose the app directly
# The Gunicorn server will handle the WSGI interface
if __name__ == "__main__":
    print("Starting in development mode...")
    port = int(os.environ.get('PORT', 8000))
    print(f"Using port: {port}")
    flask_app.run(host='0.0.0.0', port=port, debug=False)
