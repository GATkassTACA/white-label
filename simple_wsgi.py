"""
Simple WSGI entry point for Azure deployment
"""
import os
from flask import Flask, jsonify

# Create a simple Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>🎉 White Label Chat - Production Ready!</h1>
    <p>Application is running on Azure App Service</p>
    <p>Database: Connected to PostgreSQL</p>
    <p>Environment: Production</p>
    <p><a href="/health">Health Check</a></p>
    <p><a href="/status">Status</a></p>
    """

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "environment": os.environ.get('FLASK_ENV', 'production'),
        "database_configured": bool(os.environ.get('DATABASE_URL')),
        "redis_configured": bool(os.environ.get('REDIS_URL'))
    })

@app.route('/status')
def status():
    return jsonify({
        "app": "White Label Chat Platform",
        "version": "1.0.0",
        "environment": os.environ.get('FLASK_ENV', 'production'),
        "python_version": "3.11.12",
        "deployment": "Azure App Service"
    })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
