"""
User Authentication and Session Management for PharmAssist
Handles user login, logout, session management, and user roles
"""

import hashlib
import secrets
import datetime
from functools import wraps
from flask import session, request, jsonify, redirect, url_for

class UserManager:
    def __init__(self, db_manager=None):
        self.db = db_manager
        self.demo_users = {
            'pharmacist': {
                'password_hash': self._hash_password('demo123'),
                'role': 'pharmacist',
                'full_name': 'Dr. Sarah Johnson',
                'email': 'pharmacist@demo.com',
                'permissions': ['pdf_process', 'view_history', 'download', 'admin_view']
            },
            'tech': {
                'password_hash': self._hash_password('demo123'),
                'role': 'pharmacy_tech',
                'full_name': 'Mike Chen',
                'email': 'tech@demo.com',
                'permissions': ['pdf_process', 'view_history', 'download']
            },
            'manager': {
                'password_hash': self._hash_password('demo123'),
                'role': 'manager',
                'full_name': 'Jennifer Adams',
                'email': 'manager@demo.com',
                'permissions': ['pdf_process', 'view_history', 'download', 'analytics', 'user_management']
            }
        }
    
    def _hash_password(self, password):
        """Hash a password with salt"""
        salt = "pharmassist_salt_2025"  # In production, use random salts
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def authenticate_user(self, username, password):
        """Authenticate a user with username/password"""
        username = username.lower().strip()
        
        # Check demo users first
        if username in self.demo_users:
            user_data = self.demo_users[username]
            if user_data['password_hash'] == self._hash_password(password):
                return {
                    'success': True,
                    'user': {
                        'username': username,
                        'role': user_data['role'],
                        'full_name': user_data['full_name'],
                        'email': user_data['email'],
                        'permissions': user_data['permissions']
                    }
                }
        
        # Check database users if database is available
        if self.db and self.db.connection:
            try:
                cursor = self.db.connection.cursor()
                cursor.execute("""
                    SELECT username, password_hash, role, full_name, email, permissions, active
                    FROM users 
                    WHERE (username = %s OR email = %s) AND active = true
                """, (username, username))
                
                user_record = cursor.fetchone()
                if user_record:
                    stored_hash = user_record[1]
                    if stored_hash == self._hash_password(password):
                        return {
                            'success': True,
                            'user': {
                                'username': user_record[0],
                                'role': user_record[2],
                                'full_name': user_record[3],
                                'email': user_record[4],
                                'permissions': user_record[5] if user_record[5] else [],
                            }
                        }
            except Exception as e:
                print(f"Database authentication error: {e}")
        
        return {'success': False, 'error': 'Invalid username or password'}
    
    def create_session(self, user_data):
        """Create a user session"""
        session['authenticated'] = True
        session['user'] = user_data
        session['login_time'] = datetime.datetime.now().isoformat()
        session['session_token'] = secrets.token_hex(16)
        
        # Log login if database is available
        if self.db and self.db.connection:
            try:
                cursor = self.db.connection.cursor()
                cursor.execute("""
                    INSERT INTO user_sessions (username, session_token, login_time, ip_address)
                    VALUES (%s, %s, %s, %s)
                """, (
                    user_data['username'],
                    session['session_token'],
                    datetime.datetime.now(),
                    request.remote_addr
                ))
            except Exception as e:
                print(f"Session logging error: {e}")
    
    def logout_user(self):
        """Logout current user and clear session"""
        username = session.get('user', {}).get('username', 'unknown')
        session_token = session.get('session_token')
        
        # Log logout if database is available
        if self.db and self.db.connection and session_token:
            try:
                cursor = self.db.connection.cursor()
                cursor.execute("""
                    UPDATE user_sessions 
                    SET logout_time = %s 
                    WHERE session_token = %s
                """, (datetime.datetime.now(), session_token))
            except Exception as e:
                print(f"Logout logging error: {e}")
        
        # Clear session
        session.clear()
        return {'success': True, 'message': 'Logged out successfully'}
    
    def is_authenticated(self):
        """Check if current user is authenticated"""
        return session.get('authenticated', False)
    
    def get_current_user(self):
        """Get current user data from session"""
        if self.is_authenticated():
            return session.get('user', {})
        return None
    
    def has_permission(self, permission):
        """Check if current user has specific permission"""
        user = self.get_current_user()
        if not user:
            return False
        return permission in user.get('permissions', [])
    
    def setup_database_tables(self):
        """Set up user-related database tables"""
        if not self.db or not self.db.connection:
            return
        
        try:
            cursor = self.db.connection.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(128) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    full_name VARCHAR(100) NOT NULL,
                    role VARCHAR(50) NOT NULL DEFAULT 'pharmacy_tech',
                    permissions TEXT[] DEFAULT ARRAY['pdf_process', 'view_history'],
                    active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    created_by VARCHAR(50)
                )
            """)
            
            # User sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) NOT NULL,
                    session_token VARCHAR(32) NOT NULL,
                    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    logout_time TIMESTAMP,
                    ip_address INET,
                    user_agent TEXT
                )
            """)
            
            # Create default admin user if none exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
            admin_count = cursor.fetchone()[0]
            
            if admin_count == 0:
                admin_password_hash = self._hash_password('PharmAdmin2025!')
                cursor.execute("""
                    INSERT INTO users (username, password_hash, email, full_name, role, permissions)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    'admin',
                    admin_password_hash,
                    'admin@pharmassist.local',
                    'System Administrator',
                    'admin',
                    ['pdf_process', 'view_history', 'download', 'analytics', 'user_management', 'admin_all']
                ))
                print("✓ Default admin user created (username: admin, password: PharmAdmin2025!)")
            
            print("✓ User authentication tables created successfully")
            
        except Exception as e:
            print(f"Error creating user tables: {e}")


def login_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_manager = getattr(request, 'user_manager', None)
        if not user_manager or not user_manager.is_authenticated():
            if request.is_json:
                return jsonify({'error': 'Authentication required', 'code': 'AUTH_REQUIRED'}), 401
            else:
                return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function


def permission_required(permission):
    """Decorator to require specific permission for routes"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_manager = getattr(request, 'user_manager', None)
            if not user_manager or not user_manager.is_authenticated():
                if request.is_json:
                    return jsonify({'error': 'Authentication required', 'code': 'AUTH_REQUIRED'}), 401
                else:
                    return redirect(url_for('login_page'))
            
            if not user_manager.has_permission(permission):
                if request.is_json:
                    return jsonify({'error': 'Insufficient permissions', 'code': 'PERMISSION_DENIED'}), 403
                else:
                    return jsonify({'error': 'Access denied - insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
