"""
Debug WSGI application to diagnose deployment issues
"""
import os
import sys
import traceback
from flask import Flask, jsonify

print("=== DEBUG WSGI STARTING ===")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"Directory contents: {os.listdir('.')}")
print(f"Python path: {sys.path}")

# Create a simple Flask app
app = Flask(__name__)

@app.route('/')
def debug_home():
    """Debug home page showing environment details"""
    try:
        # Try to import our modules
        import_results = {}
        
        # Test basic imports
        try:
            import flask
            import_results['flask'] = f"✅ {flask.__version__}"
        except Exception as e:
            import_results['flask'] = f"❌ {e}"
        
        try:
            import psycopg2
            import_results['psycopg2'] = "✅ Available"
        except Exception as e:
            import_results['psycopg2'] = f"❌ {e}"
        
        try:
            import redis
            import_results['redis'] = "✅ Available"
        except Exception as e:
            import_results['redis'] = f"❌ {e}"
        
        # Test our app modules
        try:
            from app import create_app
            import_results['app.create_app'] = "✅ Available"
        except Exception as e:
            import_results['app.create_app'] = f"❌ {e}"
        
        try:
            import config
            import_results['config'] = "✅ Available"
        except Exception as e:
            import_results['config'] = f"❌ {e}"
        
        try:
            from models import db
            import_results['models.db'] = "✅ Available"
        except Exception as e:
            import_results['models.db'] = f"❌ {e}"
        
        # Environment variables
        env_vars = {
            'DATABASE_URL': bool(os.environ.get('DATABASE_URL')),
            'REDIS_URL': bool(os.environ.get('REDIS_URL')),
            'SECRET_KEY': bool(os.environ.get('SECRET_KEY')),
            'FLASK_ENV': os.environ.get('FLASK_ENV', 'Not Set'),
            'PORT': os.environ.get('PORT', 'Not Set')
        }
        
        return f"""
        <h1>🔍 White Label Chat - Debug Information</h1>
        
        <h2>📁 File System</h2>
        <p><strong>Working Directory:</strong> {os.getcwd()}</p>
        <p><strong>Directory Contents:</strong></p>
        <ul>
            {''.join([f'<li>{item}</li>' for item in os.listdir('.')])}
        </ul>
        
        <h2>🐍 Python Environment</h2>
        <p><strong>Python Version:</strong> {sys.version}</p>
        <p><strong>Python Path:</strong></p>
        <ul>
            {''.join([f'<li>{path}</li>' for path in sys.path])}
        </ul>
        
        <h2>📦 Import Status</h2>
        <ul>
            {''.join([f'<li><strong>{module}:</strong> {status}</li>' for module, status in import_results.items()])}
        </ul>
        
        <h2>🌍 Environment Variables</h2>
        <ul>
            {''.join([f'<li><strong>{key}:</strong> {value}</li>' for key, value in env_vars.items()])}
        </ul>
        
        <h2>🔗 Test Links</h2>
        <ul>
            <li><a href="/health">Health Check</a></li>
            <li><a href="/test-db">Test Database Connection</a></li>
            <li><a href="/test-redis">Test Redis Connection</a></li>
        </ul>
        """
        
    except Exception as e:
        return f"""
        <h1>❌ Debug Page Error</h1>
        <p><strong>Error:</strong> {str(e)}</p>
        <pre>{traceback.format_exc()}</pre>
        """

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "debug_mode",
        "working_directory": os.getcwd(),
        "python_version": sys.version,
        "environment": {
            "DATABASE_URL": bool(os.environ.get('DATABASE_URL')),
            "REDIS_URL": bool(os.environ.get('REDIS_URL')),
            "FLASK_ENV": os.environ.get('FLASK_ENV'),
            "PORT": os.environ.get('PORT')
        }
    })

@app.route('/test-db')
def test_db():
    """Test database connection"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            return jsonify({"error": "DATABASE_URL not configured"})
        
        import psycopg2
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "database_version": version[0] if version else "Unknown",
            "database_url_configured": True
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        })

@app.route('/test-redis')
def test_redis():
    """Test Redis connection"""
    try:
        redis_url = os.environ.get('REDIS_URL')
        if not redis_url:
            return jsonify({"error": "REDIS_URL not configured"})
        
        import redis
        r = redis.from_url(redis_url)
        r.ping()
        
        return jsonify({
            "status": "success",
            "redis_url_configured": True,
            "ping_successful": True
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        })

@app.route('/test-app-creation')
def test_app_creation():
    """Test creating the actual app"""
    try:
        from app import create_app
        flask_app, socketio = create_app()
        
        return jsonify({
            "status": "success",
            "app_created": True,
            "app_name": flask_app.name,
            "socketio_created": bool(socketio)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting debug server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)

print("=== DEBUG WSGI LOADED ===")
