import os
import datetime
import logging
from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
import uuid

# Database imports (optional - graceful degradation)
try:
    import psycopg2
    import psycopg2.extras
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print("Database functionality not available - running in file-only mode")

# PDF processing imports (optional - graceful degradation)
try:
    from pdf_processing import PDFProcessor
    PDF_PROCESSING_AVAILABLE = True
except ImportError:
    PDF_PROCESSING_AVAILABLE = False
    print("PDF processing libraries not available - running in demo mode")

class DatabaseManager:
    def __init__(self, app=None):
        self.app = app
        self.connection = None
        
    def init_app(self, app):
        self.app = app
        if DATABASE_AVAILABLE:
            self.connect()
            self.create_tables()
    
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            database_url = os.getenv('DATABASE_URL')
            if database_url:
                self.connection = psycopg2.connect(database_url)
            else:
                # Fallback to individual environment variables
                self.connection = psycopg2.connect(
                    host=os.getenv('DATABASE_HOST', 'localhost'),
                    database=os.getenv('DATABASE_NAME', 'pharmassist_db'),
                    user=os.getenv('DATABASE_USER', 'pharmadmin'),
                    password=os.getenv('DATABASE_PASSWORD', '')
                )
            self.connection.autocommit = True
            print("✓ Database connected successfully")
        except Exception as e:
            print(f"Database connection failed: {e}")
            self.connection = None
    
    def create_tables(self):
        """Create necessary database tables"""
        if not self.connection:
            return
            
        try:
            cursor = self.connection.cursor()
            
            # Create processing history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processing_history (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255),
                    filename VARCHAR(255),
                    original_filename VARCHAR(255),
                    processing_method VARCHAR(50),
                    status VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processing_time_seconds FLOAT,
                    file_size_bytes INTEGER,
                    extracted_text TEXT,
                    converted_data JSONB
                )
            """)
            
            # Create medication database table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS medications (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) UNIQUE,
                    generic_name VARCHAR(255),
                    drug_class VARCHAR(255),
                    common_dosages TEXT[],
                    caretend_code VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert some sample medications
            cursor.execute("""
                INSERT INTO medications (name, generic_name, drug_class, common_dosages, caretend_code)
                VALUES 
                    ('Lisinopril', 'lisinopril', 'ACE Inhibitor', ARRAY['5mg', '10mg', '20mg'], 'ACE001'),
                    ('Metformin', 'metformin', 'Diabetes', ARRAY['500mg', '850mg', '1000mg'], 'DIA001'),
                    ('Atorvastatin', 'atorvastatin', 'Statin', ARRAY['10mg', '20mg', '40mg', '80mg'], 'STA001')
                ON CONFLICT (name) DO NOTHING
            """)
            
            print("✓ Database tables created successfully")
            
        except Exception as e:
            print(f"Error creating tables: {e}")
    
    def log_processing(self, session_id, filename, original_filename, method, status, 
                      processing_time=None, file_size=None, extracted_text=None, converted_data=None):
        """Log processing activity to database"""
        if not self.connection:
            return
            
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO processing_history 
                (session_id, filename, original_filename, processing_method, status, 
                 processing_time_seconds, file_size_bytes, extracted_text, converted_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (session_id, filename, original_filename, method, status, 
                  processing_time, file_size, extracted_text, converted_data))
        except Exception as e:
            print(f"Error logging processing: {e}")
    
    def get_processing_history(self, session_id, limit=50):
        """Get processing history for a session"""
        if not self.connection:
            return []
            
        try:
            cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""
                SELECT * FROM processing_history 
                WHERE session_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (session_id, limit))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting history: {e}")
            return []

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'pharmassist-secure-key-2025')
    
    # Configure upload settings
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize database
    db = DatabaseManager()
    db.init_app(app)
    
    # Initialize PDF processor
    if PDF_PROCESSING_AVAILABLE:
        pdf_processor = PDFProcessor()
    else:
        pdf_processor = None
    
    @app.route('/')
    def index():
        """Main application page"""
        # Initialize session
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        
        # Get processing history if database is available
        history = []
        if DATABASE_AVAILABLE and db.connection:
            history = db.get_processing_history(session['session_id'])
        
        return render_template('index.html', 
                             pdf_available=PDF_PROCESSING_AVAILABLE,
                             database_available=DATABASE_AVAILABLE,
                             history=history)
    
    @app.route('/upload', methods=['POST'])
    def upload_file():
        """Handle PDF file upload and processing"""
        start_time = datetime.datetime.now()
        
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file uploaded'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not file.filename.lower().endswith('.pdf'):
                return jsonify({'error': 'Only PDF files are allowed'}), 400
            
            # Secure filename and save
            original_filename = file.filename
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Get file size
            file_size = os.path.getsize(filepath)
            
            # Get processing method from request
            method = request.form.get('method', 'auto')
            
            # Process the PDF
            if PDF_PROCESSING_AVAILABLE and pdf_processor:
                try:
                    result = pdf_processor.process_pdf(filepath, method)
                    status = 'success'
                    
                    # Processing time
                    processing_time = (datetime.datetime.now() - start_time).total_seconds()
                    
                    # Log to database
                    if DATABASE_AVAILABLE and db.connection:
                        db.log_processing(
                            session['session_id'], filename, original_filename, 
                            method, status, processing_time, file_size,
                            result.get('extracted_text', ''), result.get('converted_data')
                        )
                    
                    # Clean up file
                    try:
                        os.remove(filepath)
                    except:
                        pass
                    
                    return jsonify(result)
                    
                except Exception as e:
                    status = 'error'
                    error_msg = str(e)
                    
                    # Log error to database
                    if DATABASE_AVAILABLE and db.connection:
                        db.log_processing(
                            session['session_id'], filename, original_filename, 
                            method, status, None, file_size, None, None
                        )
                    
                    return jsonify({'error': f'Processing failed: {error_msg}'}), 500
            else:
                # Demo mode - simulate processing
                demo_result = {
                    'method_used': 'demo',
                    'extracted_text': f'DEMO MODE - File "{original_filename}" uploaded successfully\\n\\nSample Medication List:\\n• Lisinopril 10mg - Take once daily\\n• Metformin 500mg - Take twice daily with meals\\n• Atorvastatin 20mg - Take once daily at bedtime',
                    'converted_data': {
                        'format': 'CareTend',
                        'medications': [
                            {'name': 'Lisinopril', 'dosage': '10mg', 'frequency': 'Once daily', 'code': 'ACE001'},
                            {'name': 'Metformin', 'dosage': '500mg', 'frequency': 'Twice daily', 'code': 'DIA001'},
                            {'name': 'Atorvastatin', 'dosage': '20mg', 'frequency': 'Once daily', 'code': 'STA001'}
                        ]
                    },
                    'processing_info': {
                        'file_size': f'{file_size:,} bytes',
                        'method': 'Demo Mode',
                        'timestamp': datetime.datetime.now().isoformat()
                    }
                }
                
                # Log demo processing
                if DATABASE_AVAILABLE and db.connection:
                    processing_time = (datetime.datetime.now() - start_time).total_seconds()
                    db.log_processing(
                        session['session_id'], filename, original_filename, 
                        'demo', 'success', processing_time, file_size,
                        demo_result['extracted_text'], demo_result['converted_data']
                    )
                
                # Clean up file
                try:
                    os.remove(filepath)
                except:
                    pass
                
                return jsonify(demo_result)
        
        except Exception as e:
            return jsonify({'error': f'Upload failed: {str(e)}'}), 500
    
    @app.route('/history')
    def get_history():
        """Get processing history for current session"""
        if 'session_id' not in session:
            return jsonify([])
        
        if DATABASE_AVAILABLE and db.connection:
            history = db.get_processing_history(session['session_id'])
            # Convert to JSON-serializable format
            history_data = []
            for record in history:
                history_data.append({
                    'id': record['id'],
                    'filename': record['original_filename'],
                    'method': record['processing_method'],
                    'status': record['status'],
                    'created_at': record['created_at'].isoformat() if record['created_at'] else None,
                    'processing_time': record['processing_time_seconds'],
                    'file_size': record['file_size_bytes']
                })
            return jsonify(history_data)
        else:
            return jsonify([])
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'pdf_processing': PDF_PROCESSING_AVAILABLE,
            'database': DATABASE_AVAILABLE and db.connection is not None,
            'timestamp': datetime.datetime.now().isoformat()
        })
    
    # API Routes for frontend compatibility
    @app.route('/api/status')
    def api_status():
        """API status endpoint for frontend"""
        return jsonify({
            'status': 'operational',
            'pdf_processing_available': PDF_PROCESSING_AVAILABLE,
            'database_available': DATABASE_AVAILABLE and db.connection is not None,
            'methods_available': ['auto', 'pypdf2', 'pdfplumber', 'ocr'] if PDF_PROCESSING_AVAILABLE else ['demo'],
            'version': '1.0.0',
            'timestamp': datetime.datetime.now().isoformat()
        })
    
    @app.route('/api/process', methods=['POST'])
    def api_process():
        """API endpoint for PDF processing - frontend compatible"""
        start_time = datetime.datetime.now()
        
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file uploaded', 'success': False}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected', 'success': False}), 400
            
            if not file.filename.lower().endswith('.pdf'):
                return jsonify({'error': 'Only PDF files are allowed', 'success': False}), 400
            
            # Secure filename and save
            original_filename = file.filename
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Get file size
            file_size = os.path.getsize(filepath)
            
            # Get processing method from request
            method = request.form.get('method', 'auto')
            
            # Process the PDF
            if PDF_PROCESSING_AVAILABLE and pdf_processor:
                try:
                    result = pdf_processor.process_pdf(filepath, method)
                    status = 'success'
                    
                    # Processing time
                    processing_time = (datetime.datetime.now() - start_time).total_seconds()
                    
                    # Log to database
                    if DATABASE_AVAILABLE and db.connection:
                        db.log_processing(
                            session['session_id'], filename, original_filename, 
                            method, status, processing_time, file_size,
                            result.get('extracted_text', ''), result.get('converted_data')
                        )
                    
                    # Clean up file
                    try:
                        os.remove(filepath)
                    except:
                        pass
                    
                    # Return API-formatted response
                    return jsonify({
                        'success': True,
                        'method_used': result.get('method_used', method),
                        'pages_processed': result.get('pages_processed'),
                        'medications_count': len(result.get('medications', [])) if result.get('medications') else None,
                        'caretend_output': result.get('converted_data'),
                        'extracted_text': result.get('extracted_text'),
                        'processing_time': processing_time,
                        'file_size': file_size,
                        'timestamp': datetime.datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    # Log error to database
                    if DATABASE_AVAILABLE and db.connection:
                        processing_time = (datetime.datetime.now() - start_time).total_seconds()
                        db.log_processing(
                            session['session_id'], filename, original_filename, 
                            method, 'error', processing_time, file_size,
                            '', str(e)
                        )
                    
                    # Clean up file
                    try:
                        os.remove(filepath)
                    except:
                        pass
                    
                    return jsonify({
                        'success': False,
                        'error': f'Processing failed: {str(e)}',
                        'method_used': method
                    }), 500
            else:
                # Demo mode - return mock data
                processing_time = (datetime.datetime.now() - start_time).total_seconds()
                
                demo_result = {
                    'success': True,
                    'method_used': 'demo_mode',
                    'pages_processed': 1,
                    'medications_count': 3,
                    'caretend_output': '''Patient: DEMO PATIENT
DOB: 01/01/1980
MRN: DEMO123

MEDICATIONS:
1. Lisinopril 10mg - Take once daily
2. Metformin 500mg - Take twice daily with meals  
3. Atorvastatin 20mg - Take once daily at bedtime

Date: ''' + datetime.datetime.now().strftime('%m/%d/%Y') + '''
Converted by PharmAssist Enterprise
''',
                    'extracted_text': 'Demo text extraction - PDF processing libraries not available',
                    'processing_time': processing_time,
                    'file_size': file_size,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'note': 'Demo mode - Install PDF processing libraries for full functionality'
                }
                
                # Log demo processing
                if DATABASE_AVAILABLE and db.connection:
                    db.log_processing(
                        session['session_id'], filename, original_filename, 
                        'demo', 'success', processing_time, file_size,
                        demo_result['extracted_text'], demo_result['caretend_output']
                    )
                
                # Clean up file
                try:
                    os.remove(filepath)
                except:
                    pass
                
                return jsonify(demo_result)
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Upload failed: {str(e)}'
            }), 500
    
    return app

# Create the application
app = create_app()

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the application
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print("🏥 PharmAssist Enterprise PDF Processing System")
    print(f"📊 Database Support: {'✓ Available' if DATABASE_AVAILABLE else '✗ Demo Mode'}")
    print(f"📄 PDF Processing: {'✓ Available' if PDF_PROCESSING_AVAILABLE else '✗ Demo Mode'}")
    print(f"🌐 Starting server on port {port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
