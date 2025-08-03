"""
Debug WSGI entry point to identify deployment issues
"""
import os
import sys
import traceback
from flask import Flask, jsonify, request

# Add curren        return jsonify({"status": "success", "message": "Redis connection successful"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})irectory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== DEBUG WSGI STARTING ===")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")
print(f"Current working directory: {os.getcwd()}")
print(f"Directory contents: {os.listdir('.')}")

# Create a simple Flask app for debugging
app = Flask(__name__)

@app.route('/')
def debug_home():
    """Debug homepage showing environment details"""
    try:
        import_status = {}
        
        # Test critical imports
        try:
            import flask
            import_status['flask'] = f"✅ {flask.__version__}"
        except Exception as e:
            import_status['flask'] = f"❌ {str(e)}"
            
        try:
            import sqlalchemy
            import_status['sqlalchemy'] = f"✅ {sqlalchemy.__version__}"
        except Exception as e:
            import_status['sqlalchemy'] = f"❌ {str(e)}"
            
        try:
            import redis
            import_status['redis'] = f"✅ {redis.__version__}"
        except Exception as e:
            import_status['redis'] = f"❌ {str(e)}"
            
        try:
            import psycopg2
            import_status['psycopg2'] = f"✅ {psycopg2.__version__}"
        except Exception as e:
            import_status['psycopg2'] = f"❌ {str(e)}"

        # Test app imports
        try:
            sys.path.insert(0, os.getcwd())
            import app
            import_status['app_module'] = "✅ Found"
        except Exception as e:
            import_status['app_module'] = f"❌ {str(e)}"
            
        try:
            import models
            import_status['models_module'] = "✅ Found"
        except Exception as e:
            import_status['models_module'] = f"❌ {str(e)}"
            
        try:
            import config
            import_status['config_module'] = "✅ Found"
        except Exception as e:
            import_status['config_module'] = f"❌ {str(e)}"

        env_vars = {
            'DATABASE_URL': '✅ Set' if os.environ.get('DATABASE_URL') else '❌ Missing',
            'REDIS_URL': '✅ Set' if os.environ.get('REDIS_URL') else '❌ Missing',
            'FLASK_ENV': os.environ.get('FLASK_ENV', 'Not Set'),
            'PORT': os.environ.get('PORT', 'Not Set'),
            'SECRET_KEY': '✅ Set' if os.environ.get('SECRET_KEY') else '❌ Missing',
        }

        return f"""
        <h1>🔍 White Label Chat - Debug Mode</h1>
        <h2>System Information</h2>
        <p><strong>Python:</strong> {sys.version}</p>
        <p><strong>Working Directory:</strong> {os.getcwd()}</p>
        <p><strong>Request Host:</strong> {request.host}</p>
        
        <h2>Directory Contents</h2>
        <ul>
        {''.join(f'<li>{item}</li>' for item in os.listdir('.'))}
        </ul>
        
        <h2>Python Import Status</h2>
        <ul>
        {''.join(f'<li><strong>{k}:</strong> {v}</li>' for k, v in import_status.items())}
        </ul>
        
        <h2>Environment Variables</h2>
        <ul>
        {''.join(f'<li><strong>{k}:</strong> {v}</li>' for k, v in env_vars.items())}
        </ul>
        
        <h2>Test Links</h2>
        <ul>
            <li><a href="/health">Health Check</a></li>
            <li><a href="/test-db">Test Database Connection</a></li>
            <li><a href="/test-redis">Test Redis Connection</a></li>
        </ul>
        """
    except Exception as e:
        return f"<h1>Error in debug page: {str(e)}</h1><pre>{traceback.format_exc()}</pre>"

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Debug WSGI is running",
        "environment": {
            "DATABASE_URL": bool(os.environ.get('DATABASE_URL')),
            "REDIS_URL": bool(os.environ.get('REDIS_URL')),
            "FLASK_ENV": os.environ.get('FLASK_ENV')
        }
    })

@app.route('/test-db')
def test_db():
    """Test database connection"""
    try:
        import psycopg2
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            return jsonify({"status": "error", "message": "DATABASE_URL not set"})
            
        # Test connection
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        cur.execute('SELECT version();')
        version = cur.fetchone()
        cur.close()
        conn.close()
        
        return jsonify({
            "status": "success", 
            "message": "Database connection successful",
            "version": version[0] if version else "Unknown"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/test-redis')
def test_redis():
    """Test Redis connection"""
    try:
        import redis
        redis_url = os.environ.get('REDIS_URL')
        if not redis_url:
            return jsonify({"status": "error", "message": "REDIS_URL not set"})
            
        # Test connection
        r = redis.from_url(redis_url)
        r.ping()
        
        return jsonify({"status": "success", "message": "Redis connection successful"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)

print("=== DEBUG WSGI READY ===")
