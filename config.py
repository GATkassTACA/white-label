import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Flask-SocketIO settings
    SOCKETIO_ASYNC_MODE = 'threading'
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"
    
    # Chat application settings
    MAX_MESSAGE_LENGTH = 1000
    MAX_ROOMS_PER_USER = 10
    MAX_USERS_PER_ROOM = 50
    MESSAGE_HISTORY_LIMIT = 100
    
    # Rate limiting
    RATE_LIMIT_MESSAGES_PER_MINUTE = 60
    RATE_LIMIT_CONNECTIONS_PER_IP = 5
    
    # Branding
    DEFAULT_BRANDING_CONFIG = {
        "company_name": "ChatSaaS",
        "primary_color": "#007bff",
        "secondary_color": "#6c757d",
        "logo_url": "/static/images/default-logo.png",
        "welcome_message": "Welcome to our chat platform!"
    }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    DEVELOPMENT = True
    
    # Relaxed settings for development
    RATE_LIMIT_MESSAGES_PER_MINUTE = 200
    RATE_LIMIT_CONNECTIONS_PER_IP = 20

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    
    # Test-specific settings
    WTF_CSRF_ENABLED = False
    MAX_USERS_PER_ROOM = 5  # Smaller for testing
    MESSAGE_HISTORY_LIMIT = 10
    SECRET_KEY = 'test-secret-key-for-testing'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    DEVELOPMENT = False
    
    # Get secret key from environment in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    if not SECRET_KEY and os.environ.get('FLASK_ENV') == 'production':
        raise ValueError("SECRET_KEY environment variable must be set in production")
    
    # Production-specific settings
    PREFERRED_URL_SCHEME = 'https'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
