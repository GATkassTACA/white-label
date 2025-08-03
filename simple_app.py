"""
Minimal Flask app for Azure App Service testing
"""
from flask import Flask, jsonify
import os
import sys

app = Flask(__name__)

@app.route('/')
def hello():
    port = os.environ.get('PORT', 'not_set')
    return f"""
    <h1>Azure App Service Test - SUCCESS!</h1>
    <p>Flask app is running successfully</p>
    <p>Environment: {os.environ.get('FLASK_ENV', 'not_set')}</p>
    <p>Python version: {sys.version}</p>
    <p>PORT env var: {port}</p>
    <p>All env vars: {dict(os.environ)}</p>
    <p><a href="/api/health">Health Check</a></p>
    """

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "message": "Minimal Flask app working",
        "environment": os.environ.get('FLASK_ENV', 'not_set'),
        "port": os.environ.get('PORT', 'not_set'),
        "all_env": dict(os.environ)
    })

# This is the WSGI application object that Gunicorn will use
application = app

if __name__ == '__main__':
    # Azure App Service provides PORT via environment variable or defaults to 8000
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting app on port {port}")
    print(f"All environment variables: {dict(os.environ)}")
    app.run(host='0.0.0.0', port=port, debug=False)
