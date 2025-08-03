from flask import Blueprint, render_template, request, jsonify, current_app
from flask_socketio import emit
import json
import os

chat_bp = Blueprint('chat', __name__)

def load_branding_config():
    """Load branding configuration from JSON file"""
    config_path = os.path.join(current_app.root_path, 'branding', 'configs.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Return default branding if config file not found
        return {
            "company_name": "ChatSaaS",
            "primary_color": "#007bff",
            "logo_url": "/static/images/default-logo.png",
            "welcome_message": "Welcome to our chat platform!"
        }

@chat_bp.route('/')
def index():
    """Main chat interface"""
    branding = load_branding_config()
    return render_template('base.html', branding=branding)

@chat_bp.route('/api/branding')
def get_branding():
    """API endpoint to get branding configuration"""
    branding = load_branding_config()
    return jsonify(branding)

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
