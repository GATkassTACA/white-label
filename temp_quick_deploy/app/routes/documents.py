from flask import Blueprint, request, jsonify, render_template, current_app, flash, redirect, url_for
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from services.document_processor import DocumentProcessor

documents_bp = Blueprint('documents', __name__, url_prefix='/documents')

# Initialize document processor
doc_processor = DocumentProcessor()

@documents_bp.route('/')
def index():
    """Document scanning interface"""
    return render_template('documents/index.html')

@documents_bp.route('/upload', methods=['POST'])
def upload_document():
    """Handle document upload and processing"""
    try:
        # Check if file was uploaded
        if 'document' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['document']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Get extraction method preference
        extraction_method = request.form.get('method', 'auto')
        
        # Read file data
        file_data = file.read()
        filename = secure_filename(file.filename)
        
        # Process the document
        result = doc_processor.extract_document_data(
            file_data=file_data,
            filename=filename,
            method=extraction_method
        )
        
        if result['success']:
            # Analyze the content
            analysis = doc_processor.analyze_document_content(result)
            result['analysis'] = analysis
            
            # Save processing result (optional - for demo purposes)
            save_processing_result(filename, result)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Processing failed: {str(e)}'
        }), 500

@documents_bp.route('/api/process', methods=['POST'])
def api_process_document():
    """API endpoint for document processing"""
    try:
        # Handle both file upload and base64 data
        if 'document' in request.files:
            file = request.files['document']
            file_data = file.read()
            filename = secure_filename(file.filename)
        elif request.json and 'file_data' in request.json:
            import base64
            file_data = base64.b64decode(request.json['file_data'])
            filename = request.json.get('filename', 'document.pdf')
        else:
            return jsonify({
                'success': False,
                'error': 'No file data provided'
            }), 400
        
        extraction_method = request.json.get('method', 'auto') if request.json else request.form.get('method', 'auto')
        
        # Process document
        result = doc_processor.extract_document_data(
            file_data=file_data,
            filename=filename,
            method=extraction_method
        )
        
        if result['success']:
            analysis = doc_processor.analyze_document_content(result)
            result['analysis'] = analysis
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@documents_bp.route('/api/supported-formats')
def get_supported_formats():
    """Get list of supported document formats"""
    return jsonify({
        'formats': doc_processor.supported_formats,
        'max_file_size_mb': doc_processor.max_file_size // (1024 * 1024),
        'extraction_methods': ['auto', 'pypdf2', 'pdfplumber', 'ocr']
    })

@documents_bp.route('/history')
def processing_history():
    """View document processing history"""
    try:
        history_file = os.path.join(current_app.root_path, '..', 'data', 'document_history.json')
        
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        return render_template('documents/history.html', history=history)
        
    except Exception as e:
        flash(f'Error loading history: {str(e)}', 'error')
        return render_template('documents/history.html', history=[])

@documents_bp.route('/api/history')
def api_get_history():
    """API endpoint to get processing history"""
    try:
        history_file = os.path.join(current_app.root_path, '..', 'data', 'document_history.json')
        
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@documents_bp.route('/demo')
def demo():
    """Demo page with sample documents"""
    return render_template('documents/demo.html')

def save_processing_result(filename: str, result: dict):
    """Save document processing result to history"""
    try:
        # Create data directory if it doesn't exist
        data_dir = os.path.join(current_app.root_path, '..', 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        history_file = os.path.join(data_dir, 'document_history.json')
        
        # Load existing history
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        # Create history entry
        entry = {
            'timestamp': datetime.now().isoformat(),
            'filename': filename,
            'file_size': result.get('file_size', 0),
            'success': result.get('success', False),
            'extraction_method': result.get('best_method', 'unknown'),
            'total_pages': result.get('metadata', {}).get('num_pages', 0),
            'total_chars': result.get('total_chars', 0),
            'total_tables': result.get('total_tables', 0),
            'processing_time': result.get('processing_time'),
            'error': result.get('error')
        }
        
        # Add to history (keep only last 100 entries)
        history.append(entry)
        history = history[-100:]
        
        # Save updated history
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
            
    except Exception as e:
        current_app.logger.error(f"Failed to save processing result: {str(e)}")

# Error handlers
@documents_bp.errorhandler(413)
def file_too_large(error):
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 10MB.'
    }), 413

@documents_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error occurred during document processing.'
    }), 500
