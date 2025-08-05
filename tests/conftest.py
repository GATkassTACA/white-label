import pytest
import json
import os
from app import create_app

@pytest.fixture(scope='module')
def app():
    """Create application for testing"""
    # Set testing environment
    os.environ['FLASK_ENV'] = 'testing'
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def sample_branding():
    """Sample branding configuration for testing"""
    return {
        "company_name": "Test Chat",
        "primary_color": "#ff0000",
        "logo_url": "/static/images/test-logo.png",
        "welcome_message": "Welcome to test chat!"
    }