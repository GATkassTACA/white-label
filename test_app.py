#!/usr/bin/env python3
"""
Minimal test app to verify Azure deployment is working
"""
import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return """
    <h1>🏥 PharmAssist - Test App Working!</h1>
    <p>This is a minimal test to verify Azure deployment.</p>
    <p><strong>Environment Check:</strong></p>
    <ul>
        <li>Python Path: Working ✅</li>
        <li>Flask: Working ✅</li>
        <li>Azure App Service: Working ✅</li>
    </ul>
    <p><a href="/health">Health Check</a></p>
    """

@app.route('/health')
def health():
    return {
        "status": "healthy",
        "message": "Test app is working correctly",
        "environment": {
            "FLASK_ENV": os.environ.get('FLASK_ENV', 'not set'),
            "DATABASE_URL": bool(os.environ.get('DATABASE_URL')),
            "SECRET_KEY": bool(os.environ.get('SECRET_KEY'))
        }
    }

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
