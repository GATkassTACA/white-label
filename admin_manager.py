from flask import render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
import hashlib
import secrets
import datetime

class AdminManager:
    def __init__(self, app, db_manager):
        self.app = app
        self.db = db_manager
        self.setup_routes()
        
    def setup_routes(self):
        """Setup admin panel routes"""
        
        @self.app.route('/admin')
        def admin_login():
            """Admin login page"""
            if self.is_admin_logged_in():
                return redirect(url_for('admin_dashboard'))
            return render_template('admin/login.html')
        
        @self.app.route('/admin/auth', methods=['POST'])
        def admin_authenticate():
            """Handle admin login"""
            username = request.form.get('username')
            password = request.form.get('password')
            
            # Simple admin authentication (in production, use proper auth)
            admin_username = "pharmadmin"
            admin_password_hash = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"  # "admin"
            
            if username == admin_username and hashlib.sha256(password.encode()).hexdigest() == admin_password_hash:
                session['admin_logged_in'] = True
                session['admin_user'] = username
                flash('Successfully logged in to admin panel', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid credentials', 'error')
                return redirect(url_for('admin_login'))
        
        @self.app.route('/admin/logout')
        def admin_logout():
            """Admin logout"""
            session.pop('admin_logged_in', None)
            session.pop('admin_user', None)
            flash('Logged out successfully', 'info')
            return redirect(url_for('admin_login'))
        
        @self.app.route('/admin/dashboard')
        @self.admin_required
        def admin_dashboard():
            """Main admin dashboard"""
            stats = self.get_system_stats()
            return render_template('admin/dashboard.html', stats=stats)
        
        @self.app.route('/admin/customers')
        @self.admin_required
        def admin_customers():
            """Customer management page"""
            customers = self.get_all_customers()
            return render_template('admin/customers.html', customers=customers)
        
        @self.app.route('/admin/users')
        @self.admin_required
        def admin_users():
            """User management page"""
            users = self.get_all_users()
            return render_template('admin/users.html', users=users)
        
        @self.app.route('/admin/create-user', methods=['POST'])
        @self.admin_required
        def admin_create_user():
            """Create new user"""
            data = request.get_json()
            result = self.create_user(data)
            return jsonify(result)
        
        @self.app.route('/admin/edit-user/<int:user_id>', methods=['POST'])
        @self.admin_required
        def admin_edit_user(user_id):
            """Edit existing user"""
            data = request.get_json()
            result = self.edit_user(user_id, data)
            return jsonify(result)
        
        @self.app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
        @self.admin_required
        def admin_delete_user(user_id):
            """Delete user"""
            result = self.delete_user(user_id)
            return jsonify(result)
        
        @self.app.route('/admin/processing-logs')
        @self.admin_required
        def admin_processing_logs():
            """Processing logs page"""
            logs = self.get_processing_logs()
            return render_template('admin/processing_logs.html', logs=logs)
        
        @self.app.route('/admin/system-config')
        @self.admin_required
        def admin_system_config():
            """System configuration page"""
            config = self.get_system_config()
            return render_template('admin/system_config.html', config=config)
        
        @self.app.route('/admin/api/stats')
        @self.admin_required
        def admin_api_stats():
            """API endpoint for dashboard stats"""
            return jsonify(self.get_system_stats())
        
        @self.app.route('/admin/api/customers', methods=['GET', 'POST'])
        @self.admin_required
        def admin_api_customers():
            """API endpoint for customer management"""
            if request.method == 'POST':
                # Create new customer
                data = request.get_json()
                result = self.create_customer(data)
                return jsonify(result)
            else:
                # Get all customers
                customers = self.get_all_customers()
                return jsonify(customers)
        
        @self.app.route('/admin/api/processing-logs')
        @self.admin_required
        def admin_api_processing_logs():
            """API endpoint for processing logs"""
            limit = request.args.get('limit', 100, type=int)
            logs = self.get_processing_logs(limit)
            return jsonify(logs)
    
    def admin_required(self, f):
        """Decorator to require admin authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not self.is_admin_logged_in():
                flash('Admin access required', 'error')
                return redirect(url_for('admin_login'))
            return f(*args, **kwargs)
        return decorated_function
    
    def is_admin_logged_in(self):
        """Check if admin is logged in"""
        return session.get('admin_logged_in', False)
    
    def get_system_stats(self):
        """Get system statistics"""
        if not self.db.connection:
            return {
                'total_customers': 0,
                'total_processing': 0,
                'today_processing': 0,
                'success_rate': 0,
                'database_status': 'disconnected'
            }
        
        try:
            cursor = self.db.connection.cursor()
            
            # Total processing count
            cursor.execute("SELECT COUNT(*) FROM processing_history")
            total_processing = cursor.fetchone()[0]
            
            # Today's processing
            cursor.execute("""
                SELECT COUNT(*) FROM processing_history 
                WHERE DATE(created_at) = CURRENT_DATE
            """)
            today_processing = cursor.fetchone()[0]
            
            # Success rate
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success
                FROM processing_history
            """)
            result = cursor.fetchone()
            success_rate = (result[1] / result[0] * 100) if result[0] > 0 else 0
            
            # Customer count (if tenants table exists)
            try:
                cursor.execute("SELECT COUNT(*) FROM tenants")
                total_customers = cursor.fetchone()[0]
            except:
                total_customers = 0
            
            return {
                'total_customers': total_customers,
                'total_processing': total_processing,
                'today_processing': today_processing,
                'success_rate': round(success_rate, 1),
                'database_status': 'connected'
            }
            
        except Exception as e:
            return {
                'total_customers': 0,
                'total_processing': 0,
                'today_processing': 0,
                'success_rate': 0,
                'database_status': f'error: {str(e)}'
            }
    
    def get_all_customers(self):
        """Get all customers"""
        if not self.db.connection:
            return []
        
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("""
                SELECT tenant_id, display_name, contact_email, subscription_type, 
                       created_at, subscription_expires
                FROM tenants 
                ORDER BY created_at DESC
            """)
            customers = []
            for row in cursor.fetchall():
                customers.append({
                    'tenant_id': row[0],
                    'display_name': row[1],
                    'contact_email': row[2],
                    'subscription_type': row[3],
                    'created_at': row[4].isoformat() if row[4] else None,
                    'subscription_expires': row[5].isoformat() if row[5] else None
                })
            return customers
        except Exception as e:
            print(f"Error getting customers: {e}")
            return []
    
    def get_processing_logs(self, limit=100):
        """Get processing logs"""
        if not self.db.connection:
            return []
        
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("""
                SELECT id, session_id, original_filename, processing_method, 
                       status, created_at, processing_time_seconds, file_size_bytes
                FROM processing_history 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (limit,))
            
            logs = []
            for row in cursor.fetchall():
                logs.append({
                    'id': row[0],
                    'session_id': row[1],
                    'filename': row[2],
                    'method': row[3],
                    'status': row[4],
                    'created_at': row[5].isoformat() if row[5] else None,
                    'processing_time': row[6],
                    'file_size': row[7]
                })
            return logs
        except Exception as e:
            print(f"Error getting logs: {e}")
            return []
    
    def get_system_config(self):
        """Get system configuration"""
        return {
            'pdf_processing_available': True,  # This would be dynamic
            'database_available': self.db.connection is not None,
            'max_file_size': '16MB',
            'allowed_methods': ['auto', 'pypdf2', 'pdfplumber', 'ocr'],
            'session_timeout': '30 minutes',
            'log_retention': '90 days'
        }
    
    def create_customer(self, data):
        """Create a new customer"""
        # This would integrate with the customer onboarding system
        try:
            # Placeholder for customer creation logic
            return {
                'success': True,
                'message': 'Customer created successfully',
                'customer_id': secrets.token_hex(8)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating customer: {str(e)}'
            }
    
    def get_all_users(self):
        """Get all users from the database"""
        if not self.db.connection:
            return []
        
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("""
                SELECT id, username, email, role, created_at, last_login, is_active
                FROM users 
                ORDER BY created_at DESC
            """)
            users = []
            for row in cursor.fetchall():
                users.append({
                    'id': row[0],
                    'username': row[1],
                    'email': row[2],
                    'role': row[3],
                    'created_at': row[4].isoformat() if row[4] else None,
                    'last_login': row[5].isoformat() if row[5] else None,
                    'is_active': row[6]
                })
            return users
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    def create_user(self, data):
        """Create a new user"""
        if not self.db.connection:
            return {'success': False, 'message': 'Database not available'}
        
        try:
            from werkzeug.security import generate_password_hash
            
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '')
            role = data.get('role', 'user')
            
            # Validation
            if not username or not email or not password:
                return {'success': False, 'message': 'Username, email, and password are required'}
            
            if len(password) < 6:
                return {'success': False, 'message': 'Password must be at least 6 characters'}
            
            # Check if user already exists
            cursor = self.db.connection.cursor()
            cursor.execute("""
                SELECT id FROM users WHERE username = %s OR email = %s
            """, (username, email))
            
            if cursor.fetchone():
                return {'success': False, 'message': 'Username or email already exists'}
            
            # Create user
            password_hash = generate_password_hash(password)
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, is_active)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (username, email, password_hash, role, True))
            
            user_id = cursor.fetchone()[0]
            self.db.connection.commit()
            
            return {
                'success': True,
                'message': f'User "{username}" created successfully',
                'user_id': user_id
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error creating user: {str(e)}'}
    
    def edit_user(self, user_id, data):
        """Edit an existing user"""
        if not self.db.connection:
            return {'success': False, 'message': 'Database not available'}
        
        try:
            cursor = self.db.connection.cursor()
            
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if not cursor.fetchone():
                return {'success': False, 'message': 'User not found'}
            
            # Build update query dynamically
            updates = []
            params = []
            
            if 'username' in data and data['username'].strip():
                updates.append("username = %s")
                params.append(data['username'].strip())
            
            if 'email' in data and data['email'].strip():
                updates.append("email = %s")
                params.append(data['email'].strip())
            
            if 'role' in data:
                updates.append("role = %s")
                params.append(data['role'])
            
            if 'is_active' in data:
                updates.append("is_active = %s")
                params.append(data['is_active'])
            
            if 'password' in data and data['password']:
                from werkzeug.security import generate_password_hash
                updates.append("password_hash = %s")
                params.append(generate_password_hash(data['password']))
            
            if not updates:
                return {'success': False, 'message': 'No fields to update'}
            
            # Execute update
            params.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(query, params)
            self.db.connection.commit()
            
            return {'success': True, 'message': 'User updated successfully'}
            
        except Exception as e:
            return {'success': False, 'message': f'Error updating user: {str(e)}'}
    
    def delete_user(self, user_id):
        """Delete a user (soft delete by setting is_active = False)"""
        if not self.db.connection:
            return {'success': False, 'message': 'Database not available'}
        
        try:
            cursor = self.db.connection.cursor()
            
            # Check if user exists and get info
            cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # Soft delete by setting is_active = False
            cursor.execute("""
                UPDATE users SET is_active = FALSE WHERE id = %s
            """, (user_id,))
            
            self.db.connection.commit()
            
            return {
                'success': True, 
                'message': f'User "{user[0]}" deactivated successfully'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error deleting user: {str(e)}'}
