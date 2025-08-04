"""
Quick Demo Server for Client Presentation
This is a simplified version for immediate client demonstration
"""
import os
from flask import Flask, render_template_string, jsonify, request

print("🚀 Starting White Label Chat - CLIENT DEMO")
print("=" * 50)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'demo-secret-key'

# Simple in-memory user store for demo
users = {
    'admin@example.com': {
        'password': 'Admin123!',
        'user_type': 'admin',
        'name': 'System Administrator'
    }
}

@app.route('/')
def index():
    """Serve the authentication interface"""
    try:
        with open('auth.html', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"""
        <html>
        <head><title>White Label Chat - Demo</title></head>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h1>🎯 White Label Chat - Client Demo</h1>
            <p><strong>Error loading auth.html:</strong> {e}</p>
            <p><a href="/admin" style="color: blue;">Go to Admin Dashboard</a></p>
            <p><a href="/health" style="color: blue;">Health Check</a></p>
        </body>
        </html>
        """

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy", 
        "environment": "client-demo",
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

@app.route('/documents')
def documents():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Document Scanner - White Label Chat</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .gradient-bg {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
        </style>
    </head>
    <body class="bg-gray-100 min-h-screen">
        <div class="gradient-bg text-white shadow-lg">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between items-center py-6">
                    <h1 class="text-3xl font-bold">📄 Document Scanner</h1>
                    <div class="flex items-center space-x-4">
                        <span class="bg-yellow-400 text-yellow-900 px-3 py-1 rounded-full text-sm font-medium">DEMO MODE</span>
                        <a href="/admin" class="text-white hover:text-yellow-200">← Back to Admin</a>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="max-w-4xl mx-auto py-8 px-4">
            <div class="bg-white rounded-lg shadow-lg p-8">
                <div class="text-center mb-8">
                    <div class="text-6xl mb-4">📄</div>
                    <h2 class="text-3xl font-bold text-gray-900 mb-4">PDF Document Scanner</h2>
                    <p class="text-gray-600 text-lg">Extract and analyze data from PDF documents with multiple processing methods</p>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                    <div class="bg-blue-50 p-6 rounded-lg">
                        <h3 class="text-xl font-semibold text-blue-900 mb-4">🚀 Features</h3>
                        <ul class="space-y-2 text-blue-800">
                            <li>✅ Drag & Drop Upload</li>
                            <li>✅ Multi-method Processing</li>
                            <li>✅ Real-time Analysis</li>
                            <li>✅ Content Extraction</li>
                            <li>✅ Table Detection</li>
                            <li>✅ OCR Support</li>
                        </ul>
                    </div>
                    
                    <div class="bg-green-50 p-6 rounded-lg">
                        <h3 class="text-xl font-semibold text-green-900 mb-4">⚡ Processing Methods</h3>
                        <ul class="space-y-2 text-green-800">
                            <li><strong>Auto:</strong> Best method chosen automatically</li>
                            <li><strong>Advanced:</strong> pdfplumber for tables</li>
                            <li><strong>Fast:</strong> PyPDF2 for quick extraction</li>
                            <li><strong>OCR:</strong> Tesseract for scanned docs</li>
                        </ul>
                    </div>
                </div>
                
                <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-8">
                    <h3 class="text-lg font-semibold text-yellow-900 mb-2">🎯 Client Demo Feature</h3>
                    <p class="text-yellow-800">This document scanner is part of the complete white-label chat platform. In production, it would be fully functional with:</p>
                    <ul class="list-disc list-inside mt-3 text-yellow-800 space-y-1">
                        <li>Full PDF text extraction and analysis</li>
                        <li>Processing history and analytics</li>
                        <li>Integration with chat workflows</li>
                        <li>Custom branding for each client</li>
                    </ul>
                </div>
                
                <div class="text-center">
                    <div class="bg-gray-100 border-2 border-dashed border-gray-300 rounded-lg p-12 mb-6">
                        <div class="text-4xl mb-4">📁</div>
                        <h4 class="text-xl font-semibold text-gray-700 mb-2">Demo Upload Area</h4>
                        <p class="text-gray-500">In production: Drag & drop PDF files here for processing</p>
                        <div class="mt-4">
                            <span class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">Supports PDF up to 10MB</span>
                        </div>
                    </div>
                    
                    <div class="flex justify-center space-x-4">
                        <a href="/admin" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg">
                            ← Back to Dashboard
                        </a>
                        <a href="/health" class="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg">
                            System Health
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    ''')

@app.route('/admin')
def admin_dashboard():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Dashboard - White Label Chat</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .gradient-bg {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
        </style>
    </head>
    <body class="bg-gray-100 min-h-screen">
        <div class="gradient-bg text-white shadow-lg">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between items-center py-6">
                    <h1 class="text-3xl font-bold">🎯 White Label Chat - Admin Dashboard</h1>
                    <div class="flex items-center space-x-4">
                        <span class="bg-yellow-400 text-yellow-900 px-3 py-1 rounded-full text-sm font-medium">DEMO MODE</span>
                        <span class="text-white opacity-90">admin@example.com</span>
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
                                <div class="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center">
                                    <span class="text-white font-bold text-xl">👥</span>
                                </div>
                            </div>
                            <div class="ml-5 w-0 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500 truncate">Total Users</dt>
                                    <dd class="text-2xl font-bold text-gray-900">1,234</dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="bg-white overflow-hidden shadow rounded-lg">
                    <div class="p-5">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <div class="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center">
                                    <span class="text-white font-bold text-xl">💬</span>
                                </div>
                            </div>
                            <div class="ml-5 w-0 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500 truncate">Messages Today</dt>
                                    <dd class="text-2xl font-bold text-gray-900">5,678</dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="bg-white overflow-hidden shadow rounded-lg">
                    <div class="p-5">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <div class="w-12 h-12 bg-purple-500 rounded-full flex items-center justify-center">
                                    <span class="text-white font-bold text-xl">🏢</span>
                                </div>
                            </div>
                            <div class="ml-5 w-0 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500 truncate">Active Clients</dt>
                                    <dd class="text-2xl font-bold text-gray-900">12</dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="mt-8 bg-white shadow overflow-hidden sm:rounded-lg">
                <div class="px-6 py-5 border-b border-gray-200">
                    <h3 class="text-lg leading-6 font-medium text-gray-900">🚀 Platform Features</h3>
                    <p class="mt-1 max-w-2xl text-sm text-gray-500">Complete white-label chat solution ready for your clients</p>
                </div>
                <div class="px-6 py-5">
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div class="text-center p-4 bg-blue-50 rounded-lg">
                            <div class="text-2xl mb-2">🔐</div>
                            <div class="font-semibold text-blue-900">Authentication</div>
                            <div class="text-sm text-blue-700">JWT & OAuth</div>
                        </div>
                        <div class="text-center p-4 bg-green-50 rounded-lg">
                            <div class="text-2xl mb-2">💬</div>
                            <div class="font-semibold text-green-900">Real-time Chat</div>
                            <div class="text-sm text-green-700">WebSocket</div>
                        </div>
                        <div class="text-center p-4 bg-purple-50 rounded-lg">
                            <div class="text-2xl mb-2">🎨</div>
                            <div class="font-semibold text-purple-900">White Label</div>
                            <div class="text-sm text-purple-700">Custom Branding</div>
                        </div>
                        <div class="text-center p-4 bg-yellow-50 rounded-lg">
                            <div class="text-2xl mb-2">📊</div>
                            <div class="font-semibold text-yellow-900">Analytics</div>
                            <div class="text-sm text-yellow-700">Full Dashboard</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="mt-8 bg-white shadow overflow-hidden sm:rounded-lg">
                <div class="px-6 py-5 border-b border-gray-200">
                    <h3 class="text-lg leading-6 font-medium text-gray-900">📈 System Status</h3>
                </div>
                <div class="px-6 py-5">
                    <div class="space-y-4">
                        <div class="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                            <span class="text-sm font-medium text-gray-700">🟢 Chat Service</span>
                            <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                Operational
                            </span>
                        </div>
                        <div class="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                            <span class="text-sm font-medium text-gray-700">🟢 Database</span>
                            <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                Operational
                            </span>
                        </div>
                        <div class="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                            <span class="text-sm font-medium text-gray-700">🟢 Redis Cache</span>
                            <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                Operational
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="mt-8 text-center">
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-6">
                    <h4 class="text-lg font-semibold text-blue-900 mb-2">🎯 Client Demo Ready!</h4>
                    <p class="text-blue-700">This platform demonstrates the complete white-label chat solution with working authentication, beautiful UI, and admin dashboard.</p>
                    <div class="mt-4">
                        <a href="/" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mr-2">
                            ← Back to Login
                        </a>
                        <a href="/documents" class="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded mr-2">
                            📄 Document Scanner
                        </a>
                        <a href="/health" class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
                            System Health
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    print("=" * 50)
    print("🌐 CLIENT DEMO URLS:")
    print("   Login Page: http://localhost:5000")
    print("   Admin Dashboard: http://localhost:5000/admin")
    print("   Health Check: http://localhost:5000/health")
    print("=" * 50)
    print("🔐 DEMO CREDENTIALS:")
    print("   Email: admin@example.com")
    print("   Password: Admin123!")
    print("=" * 50)
    print("🎯 READY FOR CLIENT PRESENTATION!")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
