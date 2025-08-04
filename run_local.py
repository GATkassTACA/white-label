"""
Local development server for white-label chat application
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🚀 Starting White Label Chat - Local Development")
print("=" * 50)

try:
    # Import your existing app structure
    from app import create_app
    from models import db, User, Client
    
    # Create Flask app
    app, socketio = create_app()
    
    # Initialize database
    with app.app_context():
        print("📦 Creating database tables...")
        db.create_all()
        
        # Check if admin user exists
        admin_user = User.query.filter_by(email='admin@example.com').first()
        if not admin_user:
            print("👤 Creating admin user...")
            # Create default client
            default_client = Client.query.filter_by(id='default').first()
            if not default_client:
                default_client = Client(
                    id='default',
                    name='Default Client',
                    domain='localhost'
                )
                db.session.add(default_client)
            
            # Create admin user
            admin_user = User(
                username='admin',
                email='admin@example.com',
                user_type='admin',
                client_id='default'
            )
            admin_user.set_password('Admin123!')
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Admin user created: admin@example.com / Admin123!")
        else:
            print("✅ Admin user already exists: admin@example.com / Admin123!")
    
    print("=" * 50)
    print("🌐 Application URLs:")
    print("   Home: http://localhost:5000")
    print("   Admin: http://localhost:5000/auth.html")
    print("   Health: http://localhost:5000/health")
    print("=" * 50)
    print("🔐 Admin Credentials:")
    print("   Email: admin@example.com")
    print("   Password: Admin123!")
    print("=" * 50)
    
    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5000, debug=True)
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("📝 Creating minimal development server...")
    
    # Fallback to simple Flask app
    from flask import Flask, jsonify, render_template_string, request
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')
    
    # Simple in-memory user store for demo
    users = {
        'admin@example.com': {
            'password': 'Admin123!',
            'user_type': 'admin',
            'name': 'System Administrator'
        }
    }
    
    @app.route('/')
    def home():
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>White Label Chat - Development</title>
            <style>
                body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
                .card { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }
                .btn { background: #007cba; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; }
                .btn:hover { background: #005a8a; }
            </style>
        </head>
        <body>
            <h1>🚀 White Label Chat - Development Server</h1>
            <p>Your local development environment is running!</p>
            
            <div class="card">
                <h3>🔐 Admin Access</h3>
                <p><strong>Email:</strong> admin@example.com</p>
                <p><strong>Password:</strong> Admin123!</p>
                <a href="/auth.html" class="btn">👤 Go to Admin Login</a>
            </div>
            
            <div class="card">
                <h3>📋 Available Routes</h3>
                <ul>
                    <li><a href="/">Home</a></li>
                    <li><a href="/auth.html">Authentication</a></li>
                    <li><a href="/health">Health Check</a></li>
                </ul>
            </div>
            
            <div class="card">
                <h3>🛠️ Development Info</h3>
                <p>Environment: Development</p>
                <p>Server: Flask Development Server</p>
                <p>Port: 5000</p>
            </div>
        </body>
        </html>
        ''')
    
    @app.route('/auth.html')
    def auth():
        try:
            with open('auth.html', 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open('auth.html', 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except FileNotFoundError:
            return '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Admin Login</title>
                <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body class="bg-gradient-to-br from-blue-500 to-purple-600 min-h-screen">
                <div class="min-h-screen flex items-center justify-center p-4">
                    <div class="bg-white bg-opacity-20 backdrop-blur-lg p-8 rounded-xl max-w-md w-full">
                        <h1 class="text-3xl font-bold text-white mb-6 text-center">Admin Login</h1>
                        <form class="space-y-4">
                            <div>
                                <input type="email" placeholder="admin@example.com" 
                                       class="w-full p-3 rounded-lg bg-white bg-opacity-20 text-white placeholder-gray-300 border border-white border-opacity-30">
                            </div>
                            <div>
                                <input type="password" placeholder="Admin123!" 
                                       class="w-full p-3 rounded-lg bg-white bg-opacity-20 text-white placeholder-gray-300 border border-white border-opacity-30">
                            </div>
                            <button type="submit" 
                                    class="w-full bg-gradient-to-r from-blue-500 to-purple-600 py-3 rounded-lg font-semibold text-white hover:from-blue-600 hover:to-purple-700">
                                Sign In
                            </button>
                        </form>
                        <div class="mt-4 text-center">
                            <a href="/" class="text-white opacity-60 hover:opacity-80">← Back to Home</a>
                        </div>
                        <div class="mt-6 text-center">
                            <div class="text-white opacity-60 text-sm">
                                <strong>Admin Login:</strong><br/>
                                Email: admin@example.com<br/>
                                Password: Admin123!
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            '''
    
    @app.route('/health')
    def health():
        return jsonify({
            "status": "healthy", 
            "environment": "development",
            "app": "white-label-chat"
        })
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if email in users and users[email]['password'] == password:
            user = users[email]
            return jsonify({
                "access_token": "demo-token-12345",
                "refresh_token": "demo-refresh-67890",
                "user": {
                    "email": email,
                    "user_type": user['user_type'],
                    "name": user['name']
                }
            })
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    
    @app.route('/api/auth/me')
    def me():
        return jsonify({
            "user": {
                "email": "admin@example.com",
                "user_type": "admin",
                "name": "System Administrator"
            }
        })
    
    @app.route('/admin')
    def admin_dashboard():
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Dashboard</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-100 min-h-screen">
            <div class="bg-white shadow">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div class="flex justify-between items-center py-6">
                        <h1 class="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
                        <div class="flex items-center space-x-4">
                            <span class="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-medium">Admin</span>
                            <span class="text-gray-700">admin@example.com</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="p-5">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                                        <span class="text-white font-bold">👥</span>
                                    </div>
                                </div>
                                <div class="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt class="text-sm font-medium text-gray-500 truncate">Total Users</dt>
                                        <dd class="text-lg font-medium text-gray-900">1,234</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="p-5">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <div class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                                        <span class="text-white font-bold">💬</span>
                                    </div>
                                </div>
                                <div class="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt class="text-sm font-medium text-gray-500 truncate">Messages Today</dt>
                                        <dd class="text-lg font-medium text-gray-900">5,678</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="p-5">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <div class="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                                        <span class="text-white font-bold">🏢</span>
                                    </div>
                                </div>
                                <div class="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt class="text-sm font-medium text-gray-500 truncate">Active Clients</dt>
                                        <dd class="text-lg font-medium text-gray-900">12</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="mt-8 bg-white shadow overflow-hidden sm:rounded-md">
                    <div class="px-4 py-5 sm:p-6">
                        <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">Quick Actions</h3>
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <button class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                                Manage Users
                            </button>
                            <button class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
                                View Analytics
                            </button>
                            <button class="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded">
                                Client Settings
                            </button>
                            <button class="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded">
                                System Logs
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="mt-8 bg-white shadow overflow-hidden sm:rounded-md">
                    <div class="px-4 py-5 sm:p-6">
                        <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">System Status</h3>
                        <div class="space-y-3">
                            <div class="flex items-center justify-between">
                                <span class="text-sm text-gray-700">Chat Service</span>
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                    Operational
                                </span>
                            </div>
                            <div class="flex items-center justify-between">
                                <span class="text-sm text-gray-700">Database</span>
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                    Operational
                                </span>
                            </div>
                            <div class="flex items-center justify-between">
                                <span class="text-sm text-gray-700">Redis Cache</span>
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                    Operational
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        ''')
    
    print("🌐 Minimal server running at: http://localhost:5000")
    print("🔐 Admin login at: http://localhost:5000/auth.html")
    
    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5000, debug=True)
