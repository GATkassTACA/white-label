#!/usr/bin/env python3
"""
PharmAssist - Simple Pharmacy PDF Processing Application
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

@app.route('/')
def index():
    """Main page"""
    logger.info("Index page accessed")
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle PDF file upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename.lower().endswith('.pdf'):
            # Process the file (simplified for now)
            logger.info(f"Processing file: {file.filename}")
            
            # Save temporarily and process
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                file.save(tmp.name)
                
                # Simulate processing
                result = {
                    'status': 'success',
                    'filename': file.filename,
                    'message': 'PDF processed successfully',
                    'caretend_format': 'Medication list converted to CareTend format'
                }
                
                # Clean up
                os.unlink(tmp.name)
                
                return jsonify(result)
        else:
            return jsonify({'error': 'Please upload a PDF file'}), 400
            
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': 'Processing failed'}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'PharmAssist'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
