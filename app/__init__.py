from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

def create_app():
    app = Flask(__name__)
    
    # Enable CORS for all routes
    CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])
    
    # Load configuration based on environment
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    if config_name == 'testing':
        from config import TestingConfig
        app.config.from_object(TestingConfig)
    elif config_name == 'production':
        from config import ProductionConfig
        app.config.from_object(ProductionConfig)
    else:
        from config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Initialize security middleware
    from app.middleware.security import init_security_middleware
    init_security_middleware(app)
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'error': 'Token has expired'}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {'error': 'Invalid token'}, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {'error': 'Authorization token is required'}, 401
    
    # Initialize database
    from models import db
    db.init_app(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Register blueprints
    from app.routes.chat import chat_bp
    app.register_blueprint(chat_bp, url_prefix='/api')
    
    from app.routes.wizard import bp as wizard_bp
    app.register_blueprint(wizard_bp, url_prefix='/api')
    
    from app.routes.documents import documents_bp
    app.register_blueprint(documents_bp, url_prefix='/api')
    
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from app.routes.frontend import frontend_bp
    app.register_blueprint(frontend_bp)
    
    # Register socket events
    from app.socket_events import register_socket_events
    register_socket_events(socketio)
    
    return app, socketio
