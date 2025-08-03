from flask import Blueprint, render_template, request, jsonify, current_app
from flask_socketio import emit
import json
import os

chat_bp = Blueprint('chat', __name__)

def load_branding_config(client=None):
    """Load branding configuration from JSON file"""
    config_path = os.path.join(current_app.root_path, 'branding', 'configs.json')
    try:
        with open(config_path, 'r') as f:
            configs = json.load(f)
            
        # If client is specified and exists, return client-specific config
        if client and client in configs:
            return configs[client]
        
        # Return default config or the old format for backward compatibility
        if 'default' in configs:
            return configs['default']
        else:
            # Backward compatibility with old single-config format
            return configs
            
    except FileNotFoundError:
        # Return default branding if config file not found
        return {
            "company_name": "ChatSaaS",
            "primary_color": "#007bff",
            "logo_url": "/static/images/default-logo.png",
            "welcome_message": "Welcome to our chat platform!"
        }

@chat_bp.route('/')
@chat_bp.route('/<client>')
def index(client=None):
    """Main chat interface"""
    branding = load_branding_config(client)
    return render_template('base.html', branding=branding, client=client)

@chat_bp.route('/api/branding')
@chat_bp.route('/api/branding/<client>')
def get_branding(client=None):
    """API endpoint to get branding configuration"""
    branding = load_branding_config(client)
    return jsonify(branding)

@chat_bp.route('/api/clients')
def get_clients():
    """API endpoint to get available client configurations"""
    config_path = os.path.join(current_app.root_path, 'branding', 'configs.json')
    try:
        with open(config_path, 'r') as f:
            configs = json.load(f)
        
        # Return list of available clients (excluding 'default')
        clients = [client for client in configs.keys() if client != 'default']
        return jsonify({
            "clients": clients,
            "count": len(clients)
        })
    except FileNotFoundError:
        return jsonify({"clients": [], "count": 0})

@chat_bp.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "white-label-chat"})

@chat_bp.route('/api/rooms')
def get_rooms():
    """Get available chat rooms"""
    # This would typically fetch from a database
    rooms = [
        {"id": "general", "name": "General Chat", "users": 5},
        {"id": "support", "name": "Support", "users": 2},
        {"id": "announcements", "name": "Announcements", "users": 12}
    ]
    return jsonify(rooms)
