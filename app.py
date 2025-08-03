"""
Standard Flask app for Azure App Service auto-detection
"""
from flask import Flask, jsonify
import os

# Standard Flask app variable name that Azure looks for
app = Flask(__name__)

@app.route('/')
def index():
    return """
    <h1>🎉 AZURE SUCCESS!</h1>
    <p>Flask app is running on Azure App Service!</p>
    <p>Auto-detection worked!</p>
    <p><a href="/health">Health Check</a></p>
    """

@app.route('/health')
def health():
    return jsonify({
        "status": "success",
        "message": "Azure auto-detection working!",
        "port": os.environ.get('PORT', 'auto-detected')
    })

# Azure App Service will auto-detect this
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
