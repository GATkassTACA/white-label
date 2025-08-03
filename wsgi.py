"""
WSGI entry point for production deployment
"""
import os
from app import create_app
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set production environment if not specified
if not os.environ.get('FLASK_ENV'):
    os.environ['FLASK_ENV'] = 'production'

# Create the Flask app and SocketIO instance
app, socketio = create_app()

# For Azure App Service, we expose the app directly
# The Gunicorn server will handle the WSGI interface
if __name__ == "__main__":
    socketio.run(app)
