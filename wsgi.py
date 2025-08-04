"""
Robust WSGI entry point for PharmAssist Enterprise
with fallback mechanisms and error handling
"""
import os
import sys
import traceback
from flask import Flask, jsonify

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🏥 Starting PharmAssist Enterprise Application...")
print(f"Python path: {sys.path}")
print(f"Current working directory: {os.getcwd()}")
print(f"Directory contents: {os.listdir('.')}")

# Set production environment
os.environ['FLASK_ENV'] = 'production'
os.environ.setdefault('SECRET_KEY', 'pharmassist-secure-key-2025')

# Try to import the full application first
app = None
error_message = None

try:
    print("Attempting to load full PharmAssist application...")
    from app import app as full_app
    app = full_app
    print("✅ Successfully loaded full PharmAssist application!")
    
except Exception as e:
    error_message = f"Full app failed: {str(e)}"
    print(f"❌ {error_message}")
    traceback.print_exc()
    
    # Fallback to working minimal app
    try:
        print("Falling back to working minimal application...")
        from working_app_01c4c4d import app as minimal_app
        app = minimal_app
        print("✅ Successfully loaded minimal fallback application!")
        
    except Exception as e2:
        error_message = f"Both apps failed. Full: {str(e)}, Minimal: {str(e2)}"
        print(f"❌ {error_message}")
        traceback.print_exc()
        
        # Final fallback - create emergency app
        print("Creating emergency fallback application...")
        app = Flask(__name__)
        
        @app.route('/')
        def emergency():
            return f"""
            <h1>🚨 PharmAssist Enterprise - Emergency Mode</h1>
            <p><strong>Error:</strong> {error_message}</p>
            <p><strong>Status:</strong> Both primary and fallback applications failed to load.</p>
            <p><strong>Directory:</strong> {os.getcwd()}</p>
            <p><strong>Files:</strong> {', '.join(os.listdir('.'))}</p>
            <p><a href="/restore">Restore Working Version</a></p>
            """
        
        @app.route('/restore')
        def restore_info():
            return jsonify({
                "status": "emergency_mode",
                "message": "Use checkpoint: CHECKPOINT-WORKING-PharmAssist-20250804-1812.zip",
                "restore_command": "az webapp deployment source config-zip --resource-group pharmassist-enterprise --name pharmassist-enterprise --src CHECKPOINT-WORKING-PharmAssist-20250804-1812.zip"
            })

# Ensure we have an app object
if app is None:
    print("❌ CRITICAL: No app object created!")
    app = Flask(__name__)
    
    @app.route('/')
    def critical_error():
        return "<h1>CRITICAL ERROR: Application failed to initialize</h1>"

print(f"Final app object: {app}")

if __name__ == "__main__":
    print("Starting in development mode...")
    port = int(os.environ.get('PORT', 8000))
    print(f"Using port: {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
