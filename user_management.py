import os
import hashlib
import secrets
import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt

# Database imports for user management
try:
    import psycopg2
    import psycopg2.extras
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

class UserManager:
    def __init__(self, db_connection):
        self.connection = db_connection
        self.create_user_tables()
    
    def create_user_tables(self):
        """Create user management tables"""
        if not self.connection:
            return
            
        try:
            cursor = self.connection.cursor()
            
            # Create tenants table (pharmacy organizations)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tenants (
                    id SERIAL PRIMARY KEY,
                    tenant_name VARCHAR(255) UNIQUE NOT NULL,
                    display_name VARCHAR(255) NOT NULL,
                    subdomain VARCHAR(100) UNIQUE,
                    logo_url VARCHAR(500),
                    primary_color VARCHAR(7) DEFAULT '#0078d4',
                    secondary_color VARCHAR(7) DEFAULT '#ffffff',
                    subscription_type VARCHAR(50) DEFAULT 'basic',
                    subscription_expires TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT true,
                    contact_email VARCHAR(255),
                    contact_phone VARCHAR(50),
                    billing_address TEXT,
                    api_key VARCHAR(255) UNIQUE
                )
            """)
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    tenant_id INTEGER REFERENCES tenants(id),
                    username VARCHAR(100) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    first_name VARCHAR(100),
                    last_name VARCHAR(100),
                    role VARCHAR(50) DEFAULT 'user',
                    is_active BOOLEAN DEFAULT true,
                    last_login TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reset_token VARCHAR(255),
                    reset_token_expires TIMESTAMP,
                    login_attempts INTEGER DEFAULT 0,
                    locked_until TIMESTAMP
                )
            """)
            
            # Create user sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    session_token VARCHAR(255) UNIQUE,
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address INET,
                    user_agent TEXT
                )
            """)
            
            # Create audit log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id SERIAL PRIMARY KEY,
                    tenant_id INTEGER REFERENCES tenants(id),
                    user_id INTEGER REFERENCES users(id),
                    action VARCHAR(100),
                    details JSONB,
                    ip_address INET,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            print("✓ User management tables created successfully")
            
        except Exception as e:
            print(f"Error creating user tables: {e}")
    
    def create_tenant(self, tenant_data):
        """Create a new pharmacy tenant"""
        try:
            cursor = self.connection.cursor()
            
            # Generate API key
            api_key = secrets.token_urlsafe(32)
            
            cursor.execute("""
                INSERT INTO tenants 
                (tenant_name, display_name, subdomain, logo_url, primary_color, 
                 secondary_color, subscription_type, subscription_expires, 
                 contact_email, contact_phone, billing_address, api_key)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                tenant_data['tenant_name'],
                tenant_data['display_name'],
                tenant_data.get('subdomain'),
                tenant_data.get('logo_url'),
                tenant_data.get('primary_color', '#0078d4'),
                tenant_data.get('secondary_color', '#ffffff'),
                tenant_data.get('subscription_type', 'basic'),
                tenant_data.get('subscription_expires'),
                tenant_data['contact_email'],
                tenant_data.get('contact_phone'),
                tenant_data.get('billing_address'),
                api_key
            ))
            
            tenant_id = cursor.fetchone()[0]
            
            return {
                'tenant_id': tenant_id,
                'api_key': api_key,
                'status': 'success'
            }
            
        except Exception as e:
            return {'error': str(e), 'status': 'error'}
    
    def create_user(self, user_data, tenant_id):
        """Create a new user for a tenant"""
        try:
            cursor = self.connection.cursor()
            
            # Hash password
            password_hash = generate_password_hash(user_data['password'])
            
            cursor.execute("""
                INSERT INTO users 
                (tenant_id, username, email, password_hash, first_name, last_name, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                tenant_id,
                user_data['username'],
                user_data['email'],
                password_hash,
                user_data.get('first_name'),
                user_data.get('last_name'),
                user_data.get('role', 'user')
            ))
            
            user_id = cursor.fetchone()[0]
            
            # Log user creation
            self.log_audit(tenant_id, None, 'user_created', {
                'new_user_id': user_id,
                'username': user_data['username']
            })
            
            return {'user_id': user_id, 'status': 'success'}
            
        except Exception as e:
            return {'error': str(e), 'status': 'error'}
    
    def authenticate_user(self, username, password, tenant_id=None):
        """Authenticate user login"""
        try:
            cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            if tenant_id:
                cursor.execute("""
                    SELECT u.*, t.tenant_name, t.display_name, t.is_active as tenant_active
                    FROM users u 
                    JOIN tenants t ON u.tenant_id = t.id
                    WHERE u.username = %s AND u.tenant_id = %s
                """, (username, tenant_id))
            else:
                cursor.execute("""
                    SELECT u.*, t.tenant_name, t.display_name, t.is_active as tenant_active
                    FROM users u 
                    JOIN tenants t ON u.tenant_id = t.id
                    WHERE u.email = %s OR u.username = %s
                """, (username, username))
            
            user = cursor.fetchone()
            
            if not user:
                return {'error': 'User not found', 'status': 'error'}
            
            # Check if user is locked
            if user['locked_until'] and user['locked_until'] > datetime.datetime.now():
                return {'error': 'Account temporarily locked', 'status': 'error'}
            
            # Check if tenant is active
            if not user['tenant_active']:
                return {'error': 'Account suspended', 'status': 'error'}
            
            # Verify password
            if check_password_hash(user['password_hash'], password):
                # Reset login attempts
                cursor.execute("""
                    UPDATE users 
                    SET login_attempts = 0, last_login = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (user['id'],))
                
                # Create session token
                session_token = secrets.token_urlsafe(32)
                expires_at = datetime.datetime.now() + datetime.timedelta(hours=8)
                
                cursor.execute("""
                    INSERT INTO user_sessions (user_id, session_token, expires_at, ip_address)
                    VALUES (%s, %s, %s, %s)
                """, (user['id'], session_token, expires_at, request.remote_addr))
                
                # Log successful login
                self.log_audit(user['tenant_id'], user['id'], 'login_success', {
                    'ip_address': request.remote_addr
                })
                
                return {
                    'status': 'success',
                    'user': dict(user),
                    'session_token': session_token
                }
            else:
                # Increment failed attempts
                cursor.execute("""
                    UPDATE users 
                    SET login_attempts = login_attempts + 1,
                        locked_until = CASE 
                            WHEN login_attempts >= 4 THEN CURRENT_TIMESTAMP + INTERVAL '30 minutes'
                            ELSE locked_until
                        END
                    WHERE id = %s
                """, (user['id'],))
                
                return {'error': 'Invalid password', 'status': 'error'}
                
        except Exception as e:
            return {'error': str(e), 'status': 'error'}
    
    def get_tenant_by_subdomain(self, subdomain):
        """Get tenant information by subdomain"""
        try:
            cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""
                SELECT * FROM tenants 
                WHERE subdomain = %s AND is_active = true
            """, (subdomain,))
            
            return cursor.fetchone()
            
        except Exception as e:
            return None
    
    def log_audit(self, tenant_id, user_id, action, details, ip_address=None):
        """Log audit events"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO audit_log (tenant_id, user_id, action, details, ip_address)
                VALUES (%s, %s, %s, %s, %s)
            """, (tenant_id, user_id, action, details, ip_address or request.remote_addr))
        except Exception as e:
            print(f"Audit log error: {e}")

def require_auth(f):
    """Authentication decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = session.get('session_token')
        if not token:
            return redirect(url_for('login'))
        
        # Validate session token
        # ... validation logic here ...
        
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Admin role decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function
