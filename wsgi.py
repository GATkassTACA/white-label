"""
WSGI entry point for production deployment
"""
import os
import sys
from app import create_app
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set production environment if not specified
if not os.environ.get('FLASK_ENV'):
    os.environ['FLASK_ENV'] = 'production'

try:
    # Create the Flask app and SocketIO instance
    flask_app, socketio = create_app()
    
    # For Azure App Service, expose the Flask app directly
    # Note: SocketIO functionality may be limited in this deployment mode
    app = flask_app
    
    print("WSGI app created successfully")
    print(f"Flask app: {app}")
    print(f"Environment: {os.environ.get('FLASK_ENV')}")
    
except Exception as e:
    print(f"Error creating WSGI app: {e}")
    import traceback
    traceback.print_exc()
    # Create a minimal Flask app as fallback
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def hello():
        return f"WSGI Error: {str(e)}"
    
    @app.route('/api/health')
    def health():
        return {"status": "error", "message": str(e)}

# For Azure App Service, we expose the app directly
# The Gunicorn server will handle the WSGI interface
if __name__ == "__main__":
    print("Starting in development mode...")
    port = int(os.environ.get('PORT', 8000))
    print(f"Using port: {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
