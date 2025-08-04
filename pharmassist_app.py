"""
PharmAssist - Core Application Foundation
Layer 1: Basic Flask app with routing structure
"""
from flask import Flask, render_template, request, jsonify, send_file
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory pattern for better organization"""
    app = Flask(__name__)
    
    # Configuration
    app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max file size
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['PROCESSED_FOLDER'] = 'processed'
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # Ensure upload directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)
    
    # Register routes
    register_routes(app)
    
    logger.info("PharmAssist application created successfully")
    return app

def register_routes(app):
    """Register all application routes"""
    
    @app.route('/')
    def index():
        """Main application page"""
        logger.info("Index page accessed")
        return render_template('index.html')
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'PharmAssist',
            'version': '2.0',
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/api/status')
    def api_status():
        """API status endpoint"""
        return jsonify({
            'api': 'active',
            'pdf_processing': 'ready',
            'caretend_conversion': 'ready'
        })

# Create app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting PharmAssist on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
