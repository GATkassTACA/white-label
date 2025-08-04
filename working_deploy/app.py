"""
Minimal production WSGI entry point for Azure deployment
"""
import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

# Set production environment
os.environ['FLASK_ENV'] = 'production'
os.environ.setdefault('SECRET_KEY', 'azure-production-secret-key')

print("🚀 Starting minimal white-label chat application...")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Enable CORS
CORS(app, origins=["*"])

@app.route('/')
def home():
    return """
    <html>
    <head><title>White Label Chat</title></head>
    <body>
        <h1>White Label Chat Platform</h1>
        <p>Welcome to the white-label chat application!</p>
        <p><a href="/auth.html">Admin Login</a></p>
        <p><a href="/health">Health Check</a></p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "app": "white-label-chat"})

@app.route('/auth.html')
def auth_page():
    try:
        with open('auth.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
        <head><title>Auth - Coming Soon</title></head>
        <body>
            <h1>Authentication System</h1>
            <p>Admin login system is being deployed...</p>
            <p><a href="/">← Back to Home</a></p>
        </body>
        </html>
        """, 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))

# For Azure App Service
application = app
