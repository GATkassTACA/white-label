"""
Production WSGI entry point for white-label chat application
Simplified version with incremental functionality
"""
import os
import sys
import traceback
from flask import Flask, render_template, jsonify, request, make_response, render_template_string
from flask_socketio import SocketIO
from flask_cors import CORS

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set production environment
os.environ['FLASK_ENV'] = 'production'
os.environ.setdefault('SECRET_KEY', 'azure-production-secret-key-change-me')

# Database configuration
if not os.environ.get('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'postgresql://dbadmin:Unicorn1982@white-label-db-km.postgres.database.azure.com:5432/postgres?sslmode=require'

# Redis configuration  
if not os.environ.get('REDIS_URL'):
    os.environ['REDIS_URL'] = 'rediss://default:uAZ9AwAAASH@white-label-redis-km.redis.cache.windows.net:6380'

print("🚀 Starting White Label Chat Production Application...")

try:
    # Test core imports
    print("📦 Testing imports...")
    import flask
    import psycopg2
    import redis
    print("✅ All imports successful")
    
    # Create Flask app
    print("🏗️ Creating Flask application...")
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    
    # Enable CORS
    CORS(app, origins=["*"])
    
    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # Test database connection
    print("🗄️ Testing database connection...")
    import psycopg2
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        conn.close()
        print("✅ Database connection successful")
        db_status = "✅ Connected"
    except Exception as e:
        print(f"⚠️ Database connection failed: {e}")
        db_status = f"❌ Error: {str(e)}"
    
    # Test Redis connection
    print("🔄 Testing Redis connection...")
    try:
        import redis
        redis_client = redis.from_url(os.environ['REDIS_URL'])
        redis_client.ping()
        print("✅ Redis connection successful")
        redis_status = "✅ Connected"
    except Exception as e:
        print(f"⚠️ Redis connection failed: {e}")
        redis_status = f"❌ Error: {str(e)}"
    
    # Routes
    @app.route('/')
    def index():
        """Serve the main chat interface"""
        try:
            # Get the frontend HTML content
            root_dir = os.path.dirname(__file__)
            frontend_dir = os.path.join(root_dir, 'frontend')
            file_path = os.path.join(frontend_dir, 'index-secure.html')
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                response = make_response(content)
                response.headers['Content-Type'] = 'text/html; charset=utf-8'
                
                # Environment-aware CSP
                host = request.host
                if host.endswith('.azurewebsites.net'):
                    connect_src = f"'self' https://{host} wss://{host}"
                else:
                    connect_src = "'self' http://localhost:5000 ws://localhost:5000"
                
                response.headers['Content-Security-Policy'] = (
                    "default-src 'self'; "
                    "script-src 'self' https://unpkg.com https://cdn.socket.io https://cdn.tailwindcss.com 'unsafe-eval'; "
                    "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; "
                    f"connect-src {connect_src}; "
                    "img-src 'self' data: https:; "
                    "font-src 'self' https:;"
                )
                
                return response
            else:
                # Fallback simple chat interface
                return render_template_string(SIMPLE_CHAT_TEMPLATE)
                
        except Exception as e:
            print(f"Error serving frontend: {e}")
            return render_template_string(SIMPLE_CHAT_TEMPLATE)
    
    @app.route('/api/health')
    def health():
        """Health check endpoint"""
        return jsonify({
            "status": "healthy",
            "service": "white-label-chat",
            "environment": os.environ.get('FLASK_ENV'),
            "database": db_status,
            "redis": redis_status,
            "version": "1.0.0-production"
        })
    
    @app.route('/status')
    def status():
        """Detailed status page"""
        return f"""
        <h1>🎯 White Label Chat - Production Status</h1>
        <h2>✅ Application Running Successfully</h2>
        
        <h3>📋 System Status</h3>
        <ul>
            <li><strong>Environment:</strong> {os.environ.get('FLASK_ENV')}</li>
            <li><strong>Database:</strong> {db_status}</li>
            <li><strong>Redis:</strong> {redis_status}</li>
            <li><strong>SocketIO:</strong> ✅ Initialized</li>
        </ul>
        
        <h3>🔗 Links</h3>
        <ul>
            <li><a href="/">Main Chat Interface</a></li>
            <li><a href="/api/health">Health Check API</a></li>
        </ul>
        
        <h3>🌐 Environment Variables</h3>
        <ul>
            <li>DATABASE_URL: {'✅ Configured' if os.environ.get('DATABASE_URL') else '❌ Missing'}</li>
            <li>REDIS_URL: {'✅ Configured' if os.environ.get('REDIS_URL') else '❌ Missing'}</li>
            <li>SECRET_KEY: {'✅ Configured' if os.environ.get('SECRET_KEY') else '❌ Missing'}</li>
        </ul>
        """
    
    # Socket.IO events
    @socketio.on('connect')
    def handle_connect():
        print(f"🔌 Client connected: {request.sid}")
        socketio.emit('message', {
            'type': 'system',
            'message': 'Welcome to White Label Chat!',
            'timestamp': '2025-08-03T23:00:00Z'
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print(f"🔌 Client disconnected: {request.sid}")
    
    @socketio.on('message')
    def handle_message(data):
        print(f"💬 Message received: {data}")
        # Echo the message back to all clients
        socketio.emit('message', {
            'type': 'user',
            'message': data.get('message', ''),
            'user': data.get('user', 'Anonymous'),
            'timestamp': data.get('timestamp', '2025-08-03T23:00:00Z')
        })
    
    print("🎉 White Label Chat Production WSGI app created successfully!")
    print(f"🌐 Flask app: {app}")
    print(f"🔧 Environment: {os.environ.get('FLASK_ENV')}")
    
except Exception as e:
    print(f"❌ Error creating production chat app: {e}")
    traceback.print_exc()
    
    # Create fallback app
    app = Flask(__name__)
    
    @app.route('/')
    def error_page():
        return f"""
        <h1>🚨 White Label Chat - Startup Error</h1>
        <p><strong>Error:</strong> {str(e)}</p>
        <p><strong>Python Path:</strong> {sys.path}</p>
        <p><strong>Working Directory:</strong> {os.getcwd()}</p>
        <p><strong>Environment:</strong></p>
        <ul>
            <li>DATABASE_URL: {'✅ Configured' if os.environ.get('DATABASE_URL') else '❌ Missing'}</li>
            <li>REDIS_URL: {'✅ Configured' if os.environ.get('REDIS_URL') else '❌ Missing'}</li>
            <li>FLASK_ENV: {os.environ.get('FLASK_ENV', 'Not Set')}</li>
        </ul>
        """

# Simple chat template fallback
SIMPLE_CHAT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>White Label Chat - Production</title>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .glass-effect { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.2); }
    </style>
</head>
<body class="gradient-bg min-h-screen flex items-center justify-center">
    <div class="glass-effect rounded-lg p-8 w-full max-w-md">
        <h1 class="text-2xl font-bold text-white mb-6">White Label Chat</h1>
        <div id="messages" class="bg-white rounded p-4 h-64 overflow-y-auto mb-4"></div>
        <div class="flex">
            <input type="text" id="messageInput" placeholder="Type a message..." 
                   class="flex-1 px-3 py-2 rounded-l border focus:outline-none">
            <button onclick="sendMessage()" class="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600">Send</button>
        </div>
    </div>

    <script>
        const socket = io();
        const messages = document.getElementById('messages');
        const messageInput = document.getElementById('messageInput');
        
        socket.on('message', function(data) {
            const div = document.createElement('div');
            div.innerHTML = `<strong>${data.user || 'System'}:</strong> ${data.message}`;
            div.className = 'mb-2 p-2 bg-gray-100 rounded';
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        });
        
        function sendMessage() {
            const message = messageInput.value.trim();
            if (message) {
                socket.emit('message', {
                    message: message,
                    user: 'User',
                    timestamp: new Date().toISOString()
                });
                messageInput.value = '';
            }
        }
        
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
"""

# For Azure App Service
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
