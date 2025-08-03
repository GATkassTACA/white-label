"""
Minimal Flask app for Azure App Service testing
"""
from flask import Flask, jsonify
import os
import sys

app = Flask(__name__)

@app.route('/')
def hello():
    return f"""
    <h1>Azure App Service Test - SUCCESS!</h1>
    <p>Flask app is running successfully</p>
    <p>Environment: {os.environ.get('FLASK_ENV', 'not_set')}</p>
    <p>Python version: {sys.version}</p>
    <p>Port: {os.environ.get('PORT', '8000')}</p>
    <p><a href="/api/health">Health Check</a></p>
    """

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "message": "Minimal Flask app working",
        "environment": os.environ.get('FLASK_ENV', 'not_set'),
        "port": os.environ.get('PORT', '8000')
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
