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
    
    # Import PDF processor
    try:
        from pdf_processing import pdf_processor
        PDF_PROCESSOR_AVAILABLE = True
    except ImportError:
        PDF_PROCESSOR_AVAILABLE = False
        logger.warning("PDF processor not available - running in demo mode")
    
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
            'pdf_processing': 'ready' if PDF_PROCESSOR_AVAILABLE else 'demo_mode',
            'caretend_conversion': 'ready',
            'supported_methods': pdf_processor.supported_methods if PDF_PROCESSOR_AVAILABLE else {}
        })
    
    @app.route('/api/process', methods=['POST'])
    def process_pdf():
        """Main PDF processing endpoint"""
        try:
            # Check if file was uploaded
            if 'file' not in request.files:
                return jsonify({'error': 'No file uploaded'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Validate file type
            if not file.filename.lower().endswith('.pdf'):
                return jsonify({'error': 'Please upload a PDF file'}), 400
            
            # Get processing method
            method = request.form.get('method', 'auto')
            
            # Read file content
            file_content = file.read()
            filename = file.filename
            
            logger.info(f"Processing file: {filename}, method: {method}, size: {len(file_content)} bytes")
            
            if PDF_PROCESSOR_AVAILABLE:
                # Process with full functionality
                result = pdf_processor.process_pdf(file_content, method, filename)
                
                if result.get('success'):
                    return jsonify({
                        'success': True,
                        'method_used': result['method_used'],
                        'pages_processed': result['pages_processed'],
                        'medications_count': result['medications_count'],
                        'caretend_output': result['caretend_output'],
                        'filename': filename,
                        'message': f'Successfully processed {filename}'
                    })
                else:
                    return jsonify({'error': result.get('error', 'Processing failed')}), 500
            else:
                # Demo mode - simulate processing
                demo_result = simulate_processing(filename, method)
                return jsonify(demo_result)
                
        except Exception as e:
            logger.error(f"Error in process_pdf: {str(e)}")
            return jsonify({'error': f'Processing failed: {str(e)}'}), 500
    
    @app.route('/api/download/<filename>')
    def download_processed(filename):
        """Download processed files"""
        try:
            file_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
            if os.path.exists(file_path):
                return send_file(file_path, as_attachment=True)
            else:
                return jsonify({'error': 'File not found'}), 404
        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            return jsonify({'error': 'Download failed'}), 500

def simulate_processing(filename: str, method: str) -> dict:
    """Simulate PDF processing for demo purposes"""
    demo_medications = [
        {'name': 'Lisinopril', 'dosage': '10 mg', 'strength': '10', 'unit': 'mg'},
        {'name': 'Metformin', 'dosage': '500 mg', 'strength': '500', 'unit': 'mg'},
        {'name': 'Atorvastatin', 'dosage': '20 mg', 'strength': '20', 'unit': 'mg'}
    ]
    
    caretend_output = f"""CareTend Format Medication List (DEMO)
Source: {filename}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Medications: {len(demo_medications)}

--- MEDICATION LIST ---

1. Medication: Lisinopril
   Dosage: 10 mg
   Status: Active
   Source: PDF Document Processing (Demo)

2. Medication: Metformin
   Dosage: 500 mg
   Status: Active
   Source: PDF Document Processing (Demo)

3. Medication: Atorvastatin
   Dosage: 20 mg
   Status: Active
   Source: PDF Document Processing (Demo)

--- END MEDICATION LIST ---

Notes:
- This is a demonstration of the processing capability
- Install PyPDF2, pdfplumber, or pytesseract for full functionality
- CareTend compatible format
"""
    
    return {
        'success': True,
        'method_used': f'{method.title()} Processing (Demo Mode)',
        'pages_processed': 2,
        'medications_count': len(demo_medications),
        'caretend_output': caretend_output,
        'filename': filename,
        'message': f'Demo processing completed for {filename}'
    }

# Create app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting PharmAssist on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
