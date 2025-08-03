from flask import Flask
from flask_socketio import SocketIO
import os

def create_app():
    app = Flask(__name__)
    
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
    
    # Register socket events
    from app.socket_events import register_socket_events
    register_socket_events(socketio)
    
    return app, socketio
