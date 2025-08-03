import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ALGORITHM = 'HS256'
    
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
    
    # Authentication settings
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_DIGITS = True
    PASSWORD_REQUIRE_SPECIAL = True
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Branding
    DEFAULT_BRANDING_CONFIG = {
        "company_name": "ChatSaaS",
        "primary_color": "#007bff",
        "secondary_color": "#6c757d",
        "logo_url": "/static/images/default-logo.png",
        "welcome_message": "Welcome to our chat platform!"
    }
    
    # Database configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    DEVELOPMENT = True
    
    # Database: SQLite for easy development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'dev_database.db'))
    
    # Relaxed settings for development
    RATE_LIMIT_MESSAGES_PER_MINUTE = 200
    RATE_LIMIT_CONNECTIONS_PER_IP = 20
    
    # Development JWT settings
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  # Longer for development
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    
    # Database: In-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Test-specific settings
    WTF_CSRF_ENABLED = False
    MAX_USERS_PER_ROOM = 5  # Smaller for testing
    MESSAGE_HISTORY_LIMIT = 10
    SECRET_KEY = 'test-secret-key-for-testing'
    JWT_SECRET_KEY = 'test-jwt-secret-key'
    
    # Fast token expiry for testing
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=1)
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    DEVELOPMENT = False
    
    # Database: PostgreSQL for production, fallback to SQLite if DATABASE_URL not set
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Fallback to SQLite for testing/development
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 'production.db'
        )
    
    # Enhanced database settings for production
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': -1,
        'pool_pre_ping': True,
        'pool_timeout': 20
    }
    
    # Get secret key from environment in production
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')
    
    # Warn if using default keys
    if SECRET_KEY == 'dev-secret-key-change-in-production':
        print("WARNING: Using default SECRET_KEY - change in production!")
    if JWT_SECRET_KEY == 'dev-jwt-secret-change-in-production':
        print("WARNING: Using default JWT_SECRET_KEY - change in production!")
    
    # Production-specific settings
    PREFERRED_URL_SCHEME = 'https'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Enhanced rate limiting for production
    RATE_LIMIT_MESSAGES_PER_MINUTE = 30
    RATE_LIMIT_CONNECTIONS_PER_IP = 10
    
    # Redis configuration for sessions and caching
    REDIS_URL = os.environ.get('REDIS_URL')
    
    # Logging configuration
    LOG_LEVEL = 'INFO'
    
    # Security headers
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
