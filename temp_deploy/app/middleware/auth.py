from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps
import re
from models import User

def auth_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            
            if not current_user_id:
                return jsonify({'error': 'Authentication required'}), 401
            
            user = User.query.get(current_user_id)
            if not user or not user.is_active:
                return jsonify({'error': 'User not found or inactive'}), 401
            
            # Add current user to request context
            request.current_user = user
            return f(*args, **kwargs)
            
        except Exception as e:
            current_app.logger.error(f"Authentication error: {str(e)}")
            return jsonify({'error': 'Authentication failed'}), 401
    
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    @auth_required
    def decorated_function(*args, **kwargs):
        user = request.current_user
        if user.user_type != 'admin':
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    
    return decorated_function

def client_access_required(client_id):
    """Decorator to require access to specific client"""
    def decorator(f):
        @wraps(f)
        @auth_required
        def decorated_function(*args, **kwargs):
            user = request.current_user
            if user.user_type != 'admin' and user.client_id != client_id:
                return jsonify({'error': 'Access denied to this client'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_email(email):
    """Validate email format"""
    if not email or len(email) > 254:
        return False
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if not password:
        return "Password is required"
    
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return "Password must be less than 128 characters"
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return "Password must contain at least one lowercase letter"
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return "Password must contain at least one uppercase letter"
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        return "Password must contain at least one number"
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return "Password must contain at least one special character"
    
    return None  # Password is valid

def validate_username(username):
    """Validate username format"""
    if not username:
        return "Username is required"
    
    if len(username) < 3:
        return "Username must be at least 3 characters long"
    
    if len(username) > 30:
        return "Username must be less than 30 characters"
    
    # Allow only alphanumeric characters, underscores, and hyphens
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return "Username can only contain letters, numbers, underscores, and hyphens"
    
    return None  # Username is valid

def get_current_user():
    """Get current authenticated user from request context"""
    return getattr(request, 'current_user', None)

def is_authenticated():
    """Check if current request is authenticated"""
    try:
        verify_jwt_in_request(optional=True)
        current_user_id = get_jwt_identity()
        return current_user_id is not None
    except:
        return False

def rate_limit_by_user(max_requests=100, window_minutes=60):
    """Rate limiting decorator by user (placeholder for future implementation)"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # TODO: Implement rate limiting logic with Redis
            # For now, just pass through
            return f(*args, **kwargs)
        return decorated_function
    return decorator
