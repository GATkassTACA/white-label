import pytest
import json
import os
from app import create_app

@pytest.fixture
def app():
    """Create application for testing"""
    # Set testing environment
    os.environ['FLASK_ENV'] = 'testing'
    
    app, socketio = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        yield app, socketio

@pytest.fixture
def client(app):
    """Create test client"""
    app, _ = app
    return app.test_client()

@pytest.fixture
def socketio_client(app):
    """Create SocketIO test client"""
    app, socketio = app
    return socketio.test_client(app)

@pytest.fixture
def sample_branding():
    """Sample branding configuration for testing"""
    return {
        "company_name": "Test Chat",
        "primary_color": "#ff0000",
        "logo_url": "/static/images/test-logo.png",
        "welcome_message": "Welcome to test chat!"
    }
