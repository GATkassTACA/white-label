import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
import uuid

class AuthService:
    """Authentication service for the chat application"""
    
    @staticmethod
    def generate_token(user_id, username):
        """Generate JWT token for authenticated user"""
        payload = {
            'user_id': user_id,
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        
        secret_key = current_app.config.get('SECRET_KEY', 'dev-secret-key')
        return jwt.encode(payload, secret_key, algorithm='HS256')
    
    @staticmethod
    def verify_token(token):
        """Verify JWT token and return user info"""
        try:
            secret_key = current_app.config.get('SECRET_KEY', 'dev-secret-key')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return {
                'user_id': payload['user_id'],
                'username': payload['username'],
                'valid': True
            }
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'Token expired'}
        except jwt.InvalidTokenError:
            return {'valid': False, 'error': 'Invalid token'}
    
    @staticmethod
    def create_guest_user():
        """Create a temporary guest user"""
        user_id = str(uuid.uuid4())
        username = f"Guest_{user_id[:8]}"
        
        return {
            'user_id': user_id,
            'username': username,
            'is_guest': True,
            'created_at': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def validate_username(username):
        """Validate username format"""
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(username) > 20:
            return False, "Username must be less than 20 characters"
        
        # Allow alphanumeric, underscore, and dash
        import re
        if not re.match("^[a-zA-Z0-9_-]+$", username):
            return False, "Username can only contain letters, numbers, underscore, and dash"
        
        return True, "Valid username"

def require_auth(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        auth_result = AuthService.verify_token(token)
        
        if not auth_result['valid']:
            return jsonify({'error': auth_result.get('error', 'Invalid token')}), 401
        
        # Add user info to request context
        request.current_user = {
            'user_id': auth_result['user_id'],
            'username': auth_result['username']
        }
        
        return f(*args, **kwargs)
    
    return decorated_function

def optional_auth(f):
    """Decorator for optional authentication (guest users allowed)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if token:
            if token.startswith('Bearer '):
                token = token[7:]
            
            auth_result = AuthService.verify_token(token)
            
            if auth_result['valid']:
                request.current_user = {
                    'user_id': auth_result['user_id'],
                    'username': auth_result['username'],
                    'is_guest': False
                }
            else:
                # Create guest user for invalid/expired tokens
                request.current_user = AuthService.create_guest_user()
        else:
            # Create guest user for no token
            request.current_user = AuthService.create_guest_user()
        
        return f(*args, **kwargs)
    
    return decorated_function
