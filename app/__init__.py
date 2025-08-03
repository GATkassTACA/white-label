from flask import Flask
from flask_socketio import SocketIO

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Register blueprints
    from app.routes import chat_bp
    app.register_blueprint(chat_bp)
    
    # Register socket events
    from app.socket_events import register_socket_events
    register_socket_events(socketio)
    
    return app, socketio
