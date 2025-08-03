"""
WSGI entry point for production deployment
"""
import os
from app import create_app
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create the Flask app and SocketIO instance
app, socketio = create_app()

if __name__ == "__main__":
    socketio.run(app)
