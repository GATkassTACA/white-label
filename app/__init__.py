from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
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
    
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Register blueprints
    from app.routes.chat import chat_bp
    app.register_blueprint(chat_bp)
    
    from app.routes.wizard import bp as wizard_bp
    app.register_blueprint(wizard_bp)
    
    from app.routes.documents import documents_bp
    app.register_blueprint(documents_bp)
    
    # Register socket events
    from app.socket_events import register_socket_events
    register_socket_events(socketio)
    
    return app, socketio
