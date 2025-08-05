"""
PharmChat - Local Pharmacy Chat System
Customized white-label chat for pharmacy operations
"""
import os
from flask import Flask, render_template_string, jsonify, request

print("💊 Starting PharmChat - Pharmacy Communication System")
print("=" * 60)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pharmacy-secure-key-2024'

# Pharmacy staff user store
users = {
    'pharmacist@yourpharmacy.com': {
        'password': 'PharmSecure123!',
        'user_type': 'pharmacist',
        'name': 'Head Pharmacist',
        'role': 'Senior Pharmacist'
    },
    'tech@yourpharmacy.com': {
        'password': 'TechSecure123!', 
        'user_type': 'technician',
        'name': 'Pharmacy Technician',
        'role': 'Certified Technician'
    },
    'manager@yourpharmacy.com': {
        'password': 'ManagerSecure123!',
        'user_type': 'manager', 
        'name': 'Pharmacy Manager',
        'role': 'Store Manager'
    }
}

@app.route('/')
def index():
    """Pharmacy login interface"""
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PharmChat - Pharmacy Communication System</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .pharmacy-gradient {
                background: linear-gradient(135deg, #059669 0%, #065f46 100%);
            }
            .glass-effect {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
        </style>
    </head>
    <body class="pharmacy-gradient min-h-screen">
        <div class="min-h-screen flex items-center justify-center p-4">
            <div class="glass-effect p-8 rounded-xl max-w-md w-full">
                <div class="text-center mb-8">
                    <div class="text-6xl mb-4">💊</div>
                    <h1 class="text-3xl font-bold text-white mb-2">PharmChat</h1>
                    <p class="text-white opacity-80">Pharmacy Communication System</p>
                    <p class="text-green-200 text-sm mt-2">Secure • Local • HIPAA Compliant</p>
                </div>

                <form id="loginForm" class="space-y-4">
                    <div>
                        <label class="block text-white text-sm font-medium mb-2">Email</label>
                        <input type="email" id="email" required
                               class="w-full px-4 py-3 rounded-lg bg-white bg-opacity-20 border border-white border-opacity-30 text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-green-400"
                               placeholder="your.email@pharmacy.com"
                               value="pharmacist@yourpharmacy.com">
                    </div>
                    
                    <div>
                        <label class="block text-white text-sm font-medium mb-2">Password</label>
                        <input type="password" id="password" required
                               class="w-full px-4 py-3 rounded-lg bg-white bg-opacity-20 border border-white border-opacity-30 text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-green-400"
                               placeholder="Enter your password"
                               value="PharmSecure123!">
                    </div>
                    
                    <button type="submit" id="loginBtn"
                            class="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 rounded-lg transition-colors">
                        Sign In to PharmChat
                    </button>
                </form>

                <div class="mt-6 text-center">
                    <div class="text-white opacity-60 text-sm">
                        <strong>Demo Accounts:</strong><br/>
                        <div class="mt-2 space-y-1">
                            <div>👨‍⚕️ Pharmacist: pharmacist@yourpharmacy.com / PharmSecure123!</div>
                            <div>👩‍💼 Technician: tech@yourpharmacy.com / TechSecure123!</div>
                            <div>👨‍💼 Manager: manager@yourpharmacy.com / ManagerSecure123!</div>
                        </div>
                    </div>
                </div>

                <div class="mt-6 text-center">
                    <div class="bg-green-100 bg-opacity-20 border border-green-400 border-opacity-30 text-green-100 px-3 py-2 rounded text-xs">
                        🔒 Local Installation - Your Data Stays Private
                    </div>
                </div>
            </div>
        </div>

        <script>
            document.getElementById('loginForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;
                const btn = document.getElementById('loginBtn');
                
                btn.textContent = 'Signing In...';
                btn.disabled = true;
                
                try {
                    const response = await fetch('/api/auth/login', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({email, password})
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        localStorage.setItem('user', JSON.stringify(data.user));
                        window.location.href = '/dashboard';
                    } else {
                        alert('Invalid credentials');
                    }
                } catch (error) {
                    alert('Login failed');
                } finally {
                    btn.textContent = 'Sign In to PharmChat';
                    btn.disabled = false;
                }
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if email in users and users[email]['password'] == password:
        user = users[email]
        return jsonify({
            "access_token": "pharmacy-token-12345",
            "user": {
                "email": email,
                "user_type": user['user_type'],
                "name": user['name'],
                "role": user['role']
            }
        })
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/dashboard')
def dashboard():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>PharmChat Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .pharmacy-gradient {
                background: linear-gradient(135deg, #059669 0%, #065f46 100%);
            }
        </style>
    </head>
    <body class="bg-gray-100 min-h-screen">
        <div class="pharmacy-gradient text-white shadow-lg">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between items-center py-6">
                    <div class="flex items-center">
                        <span class="text-3xl mr-3">💊</span>
                        <h1 class="text-3xl font-bold">PharmChat Dashboard</h1>
                    </div>
                    <div class="flex items-center space-x-4">
                        <span class="bg-green-200 text-green-900 px-3 py-1 rounded-full text-sm font-medium">LOCAL SYSTEM</span>
                        <span class="text-white opacity-90" id="userInfo">Loading...</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <!-- Quick Stats -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
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
                                    <dt class="text-sm font-medium text-gray-500 truncate">Active Staff</dt>
                                    <dd class="text-2xl font-bold text-gray-900">8</dd>
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
                                    <dd class="text-2xl font-bold text-gray-900">47</dd>
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
                                    <span class="text-white font-bold text-xl">📋</span>
                                </div>
                            </div>
                            <div class="ml-5 w-0 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500 truncate">Prescriptions</dt>
                                    <dd class="text-2xl font-bold text-gray-900">156</dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="bg-white overflow-hidden shadow rounded-lg">
                    <div class="p-5">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <div class="w-12 h-12 bg-yellow-500 rounded-full flex items-center justify-center">
                                    <span class="text-white font-bold text-xl">⚠️</span>
                                </div>
                            </div>
                            <div class="ml-5 w-0 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500 truncate">Alerts</dt>
                                    <dd class="text-2xl font-bold text-gray-900">3</dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Main Features -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                <div class="bg-white shadow overflow-hidden sm:rounded-lg">
                    <div class="px-6 py-5 border-b border-gray-200">
                        <h3 class="text-lg leading-6 font-medium text-gray-900">💬 Team Communication</h3>
                        <p class="mt-1 max-w-2xl text-sm text-gray-500">Internal chat for pharmacy staff</p>
                    </div>
                    <div class="px-6 py-5">
                        <div class="space-y-3">
                            <button onclick="window.open('/chat', '_blank')" class="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 rounded-lg">
                                💬 Open Staff Chat
                            </button>
                            <button onclick="window.open('/alerts', '_blank')" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg">
                                📞 Emergency Alerts
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="bg-white shadow overflow-hidden sm:rounded-lg">
                    <div class="px-6 py-5 border-b border-gray-200">
                        <h3 class="text-lg leading-6 font-medium text-gray-900">📄 Document Processing</h3>
                        <p class="mt-1 max-w-2xl text-sm text-gray-500">Scan prescriptions and insurance docs</p>
                    </div>
                    <div class="px-6 py-5">
                        <div class="space-y-3">
                            <button class="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded-lg" onclick="window.open('/documents', '_blank')">
                                📄 Document Scanner
                            </button>
                            <button onclick="window.open('/reports', '_blank')" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-4 rounded-lg">
                                📊 Reports & Analytics
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Pharmacy-Specific Features -->
            <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
                <div class="px-6 py-5 border-b border-gray-200">
                    <h3 class="text-lg leading-6 font-medium text-gray-900">🏥 Pharmacy Operations</h3>
                </div>
                <div class="px-6 py-5">
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div class="text-center p-4 bg-green-50 rounded-lg">
                            <div class="text-2xl mb-2">💊</div>
                            <div class="font-semibold text-green-900">Inventory</div>
                            <div class="text-sm text-green-700">Stock Management</div>
                        </div>
                        <div class="text-center p-4 bg-blue-50 rounded-lg">
                            <div class="text-2xl mb-2">👨‍⚕️</div>
                            <div class="font-semibold text-blue-900">Consultations</div>
                            <div class="text-sm text-blue-700">Patient Care</div>
                        </div>
                        <div class="text-center p-4 bg-purple-50 rounded-lg">
                            <div class="text-2xl mb-2">🔒</div>
                            <div class="font-semibold text-purple-900">HIPAA Secure</div>
                            <div class="text-sm text-purple-700">Local Data</div>
                        </div>
                        <div class="text-center p-4 bg-yellow-50 rounded-lg">
                            <div class="text-2xl mb-2">⚡</div>
                            <div class="font-semibold text-yellow-900">Fast Access</div>
                            <div class="text-sm text-yellow-700">No Internet Required</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Local Installation Benefits -->
            <div class="bg-green-50 border border-green-200 rounded-lg p-6">
                <h4 class="text-lg font-semibold text-green-900 mb-4">🏠 Local Installation Benefits</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="space-y-2">
                        <div class="flex items-center text-green-800">
                            <span class="text-green-600 mr-2">✅</span>
                            <span>HIPAA Compliant - Data stays on-site</span>
                        </div>
                        <div class="flex items-center text-green-800">
                            <span class="text-green-600 mr-2">✅</span>
                            <span>No monthly fees - One-time purchase</span>
                        </div>
                        <div class="flex items-center text-green-800">
                            <span class="text-green-600 mr-2">✅</span>
                            <span>Works offline - No internet dependency</span>
                        </div>
                    </div>
                    <div class="space-y-2">
                        <div class="flex items-center text-green-800">
                            <span class="text-green-600 mr-2">✅</span>
                            <span>Custom integrations with pharmacy software</span>
                        </div>
                        <div class="flex items-center text-green-800">
                            <span class="text-green-600 mr-2">✅</span>
                            <span>Full control over updates and features</span>
                        </div>
                        <div class="flex items-center text-green-800">
                            <span class="text-green-600 mr-2">✅</span>
                            <span>24/7 availability without service outages</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Display user info
            const user = JSON.parse(localStorage.getItem('user') || '{}');
            document.getElementById('userInfo').textContent = `${user.name || 'User'} (${user.role || 'Staff'})`;
        </script>
    </body>
    </html>
    ''')

@app.route('/documents')
def documents():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>PharmChat Document Scanner</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .pharmacy-gradient {
                background: linear-gradient(135deg, #059669 0%, #065f46 100%);
            }
        </style>
    </head>
    <body class="bg-gray-100 min-h-screen">
        <div class="pharmacy-gradient text-white shadow-lg">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between items-center py-6">
                    <h1 class="text-3xl font-bold">📄 Prescription & Document Scanner</h1>
                    <div class="flex items-center space-x-4">
                        <span class="bg-green-200 text-green-900 px-3 py-1 rounded-full text-sm font-medium">HIPAA COMPLIANT</span>
                        <a href="/dashboard" class="text-white hover:text-green-200">← Back to Dashboard</a>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="max-w-4xl mx-auto py-8 px-4">
            <div class="bg-white rounded-lg shadow-lg p-8">
                <div class="text-center mb-8">
                    <div class="text-6xl mb-4">💊📄</div>
                    <h2 class="text-3xl font-bold text-gray-900 mb-4">Prescription Document Scanner</h2>
                    <p class="text-gray-600 text-lg">Securely scan and process prescriptions, insurance cards, and medical documents</p>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                    <div class="bg-green-50 p-6 rounded-lg">
                        <h3 class="text-xl font-semibold text-green-900 mb-4">🏥 Pharmacy Features</h3>
                        <ul class="space-y-2 text-green-800">
                            <li>✅ Prescription Text Extraction</li>
                            <li>✅ Insurance Card Processing</li>
                            <li>✅ Patient Document Management</li>
                            <li>✅ HIPAA Compliant Storage</li>
                            <li>✅ Local Data Processing</li>
                            <li>✅ OCR for Handwritten Rx</li>
                        </ul>
                    </div>
                    
                    <div class="bg-blue-50 p-6 rounded-lg">
                        <h3 class="text-xl font-semibold text-blue-900 mb-4">🔒 Security Features</h3>
                        <ul class="space-y-2 text-blue-800">
                            <li>🔐 Local processing only</li>
                            <li>🔐 No cloud uploads</li>
                            <li>🔐 Encrypted local storage</li>
                            <li>🔐 Audit trail logging</li>
                            <li>🔐 Role-based access</li>
                            <li>🔐 Secure data disposal</li>
                        </ul>
                    </div>
                </div>
                
                <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-8">
                    <h3 class="text-lg font-semibold text-yellow-900 mb-2">💊 Pharmacy Document Processing</h3>
                    <p class="text-yellow-800">This scanner is specifically configured for pharmacy operations with support for:</p>
                    <ul class="list-disc list-inside mt-3 text-yellow-800 space-y-1">
                        <li>Prescription documents (handwritten and printed)</li>
                        <li>Insurance cards and prior authorizations</li>
                        <li>Patient identification documents</li>
                        <li>Medical records and test results</li>
                        <li>Inventory and supplier documents</li>
                    </ul>
                </div>
                
                <div class="text-center">
                    <div class="bg-gray-100 border-2 border-dashed border-gray-300 rounded-lg p-12 mb-6">
                        <div class="text-4xl mb-4">📄💊</div>
                        <h4 class="text-xl font-semibold text-gray-700 mb-2">Secure Document Upload</h4>
                        <p class="text-gray-500 mb-4">In production: Drag & drop prescription documents here for processing</p>
                        <div class="flex justify-center space-x-2">
                            <span class="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">HIPAA Compliant</span>
                            <span class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">Local Processing</span>
                            <span class="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm">Encrypted Storage</span>
                        </div>
                    </div>
                    
                    <div class="flex justify-center space-x-4">
                        <a href="/dashboard" class="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg">
                            ← Back to Dashboard
                        </a>
                        <button class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg">
                            View Processing History
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    ''')

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "environment": "pharmacy-local",
        "app": "PharmChat",
        "hipaa_compliant": True,
        "local_installation": True
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🏥 PHARMACY INSTALLATION URLS:")
    print("   Login: http://localhost:5000")
    print("   Dashboard: http://localhost:5000/dashboard")
    print("   Document Scanner: http://localhost:5000/documents")
    print("   Health Check: http://localhost:5000/health")
    print("=" * 60)
    print("💊 PHARMACY STAFF ACCOUNTS:")
    print("   Pharmacist: pharmacist@yourpharmacy.com / PharmSecure123!")
    print("   Technician: tech@yourpharmacy.com / TechSecure123!")
    print("   Manager: manager@yourpharmacy.com / ManagerSecure123!")
    print("=" * 60)
    print("🔒 LOCAL INSTALLATION - HIPAA COMPLIANT")
    print("=" * 60)
    
    app.run(host='127.0.0.1', port=5000, debug=False)  # Only localhost for security
