"""
Minimal test WSGI application for Azure deployment
"""
import os
from flask import Flask

print("=== MINIMAL TEST APP STARTING ===")
print(f"Working directory: {os.getcwd()}")
print(f"Directory contents: {os.listdir('.')}")
print(f"PORT environment variable: {os.environ.get('PORT', 'Not Set')}")

app = Flask(__name__)

@app.route('/')
def hello():
    return f"""
    <h1>✅ Minimal Test App Working!</h1>
    <p><strong>Working Directory:</strong> {os.getcwd()}</p>
    <p><strong>Port:</strong> {os.environ.get('PORT', 'Not Set')}</p>
    <p><strong>Directory Contents:</strong></p>
    <ul>
        {''.join([f'<li>{item}</li>' for item in os.listdir('.')])}
    </ul>
    """

@app.route('/health')
def health():
    return {"status": "ok", "app": "minimal_test"}

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting minimal test app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)

print("=== MINIMAL TEST APP LOADED ===")
