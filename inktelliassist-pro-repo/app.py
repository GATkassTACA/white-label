"""
TattooAssist Enterprise - AI Document Processing for Tattoo Parlors
Based on PharmAssist architecture, customized for tattoo industry
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib
import secrets
from functools import wraps
import PyPDF2
import pdfplumber
import io
import time
import re
import json

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Industry-specific configuration
INDUSTRY_CONFIG = {
    'name': 'InktelliAssist Pro',
    'tagline': 'Professional Intelligence for Ink Artists',
    'industry': 'tattoo',
    'brand_color': '#000000',  # Deep black (classic tattoo)
    'accent_color': '#DC143C',  # Crimson red
    'highlight_color': '#00BFFF',  # Electric blue
    'document_types': [
        'consent_forms',
        'aftercare_instructions', 
        'health_questionnaires',
        'design_contracts',
        'photo_releases',
        'payment_agreements'
    ],
    'processing_fields': [
        'client_name',
        'client_age', 
        'tattoo_location',
        'tattoo_size',
        'design_description',
        'allergies',
        'medications',
        'health_conditions',
        'artist_name',
        'session_date',
        'pricing',
        'aftercare_provided'
    ]
}

# Database Configuration
DATABASE_CONFIG = {
    'host': os.environ.get('DATABASE_HOST', 'localhost'),
    'database': os.environ.get('DATABASE_NAME', 'tattooassist_db'),
    'user': os.environ.get('DATABASE_USER', 'tattooassist_admin'),
    'password': os.environ.get('DATABASE_PASSWORD', 'your_password_here'),
    'port': os.environ.get('DATABASE_PORT', '5432')
}

class DatabaseManager:
    def __init__(self):
        self.config = DATABASE_CONFIG
        
    def get_connection(self):
        """Get database connection with proper error handling"""
        try:
            conn = psycopg2.connect(**self.config)
            return conn
        except psycopg2.Error as e:
            app.logger.error(f"Database connection error: {e}")
            return None
    
    def init_tables(self):
        """Initialize database tables for tattoo parlor"""
        conn = self.get_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(80) UNIQUE NOT NULL,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    password_hash VARCHAR(128) NOT NULL,
                    role VARCHAR(20) DEFAULT 'artist',
                    parlor_name VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Clients table (tattoo-specific)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    client_name VARCHAR(100) NOT NULL,
                    client_email VARCHAR(120),
                    client_phone VARCHAR(20),
                    date_of_birth DATE,
                    emergency_contact VARCHAR(100),
                    emergency_phone VARCHAR(20),
                    allergies TEXT,
                    medications TEXT,
                    health_conditions TEXT,
                    previous_tattoos BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tattoo sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tattoo_sessions (
                    id SERIAL PRIMARY KEY,
                    client_id INTEGER REFERENCES clients(id),
                    artist_id INTEGER REFERENCES users(id),
                    session_date DATE NOT NULL,
                    tattoo_location VARCHAR(100),
                    tattoo_size VARCHAR(50),
                    design_description TEXT,
                    estimated_hours DECIMAL(4,2),
                    hourly_rate DECIMAL(8,2),
                    total_price DECIMAL(10,2),
                    deposit_paid DECIMAL(10,2),
                    status VARCHAR(20) DEFAULT 'scheduled',
                    aftercare_given BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Document processing table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_processing (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    client_id INTEGER REFERENCES clients(id),
                    document_type VARCHAR(50) NOT NULL,
                    filename VARCHAR(255) NOT NULL,
                    extracted_data JSONB,
                    processing_time DECIMAL(6,3),
                    processing_method VARCHAR(20),
                    confidence_score DECIMAL(4,3),
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'completed'
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
            
        except psycopg2.Error as e:
            app.logger.error(f"Database initialization error: {e}")
            if conn:
                conn.close()
            return False

# Initialize database manager
db_manager = DatabaseManager()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

class TattooDocumentProcessor:
    """AI Document Processing specialized for tattoo parlors"""
    
    def __init__(self):
        self.supported_types = INDUSTRY_CONFIG['document_types']
        self.extraction_fields = INDUSTRY_CONFIG['processing_fields']
    
    def process_document(self, file_content, filename):
        """Process tattoo parlor documents with AI extraction"""
        start_time = time.time()
        
        try:
            # Try multiple extraction methods
            text = self.extract_text_advanced(file_content)
            
            if not text or len(text.strip()) < 10:
                text = self.extract_text_basic(file_content)
            
            if not text or len(text.strip()) < 10:
                return {
                    'success': False,
                    'error': 'Could not extract readable text from document',
                    'processing_time': time.time() - start_time
                }
            
            # Extract structured data
            extracted_data = self.extract_tattoo_data(text, filename)
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'extracted_data': extracted_data,
                'raw_text': text[:500] + '...' if len(text) > 500 else text,
                'processing_time': round(processing_time, 3),
                'processing_method': 'ai_extraction',
                'confidence_score': self.calculate_confidence(extracted_data)
            }
            
        except Exception as e:
            app.logger.error(f"Document processing error: {e}")
            return {
                'success': False,
                'error': f'Processing failed: {str(e)}',
                'processing_time': time.time() - start_time
            }
    
    def extract_text_advanced(self, file_content):
        """Advanced text extraction using pdfplumber"""
        try:
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text
        except:
            return None
    
    def extract_text_basic(self, file_content):
        """Basic text extraction using PyPDF2"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except:
            return None
    
    def extract_tattoo_data(self, text, filename):
        """Extract tattoo-specific data using AI patterns"""
        data = {
            'document_type': self.identify_document_type(filename, text),
            'extraction_timestamp': datetime.now().isoformat()
        }
        
        # Client information extraction
        name_match = re.search(r'(?:name|client)[:\s]*([A-Za-z\s]{2,50})', text, re.IGNORECASE)
        if name_match:
            data['client_name'] = name_match.group(1).strip()
        
        # Age extraction
        age_match = re.search(r'(?:age|born)[:\s]*(\d{1,3})', text, re.IGNORECASE)
        if age_match:
            data['client_age'] = int(age_match.group(1))
        
        # Tattoo location
        location_patterns = [
            r'(?:location|placement|area)[:\s]*([A-Za-z\s]{2,30})',
            r'(?:arm|leg|back|chest|shoulder|ankle|wrist|neck|face)'
        ]
        for pattern in location_patterns:
            location_match = re.search(pattern, text, re.IGNORECASE)
            if location_match:
                data['tattoo_location'] = location_match.group(1).strip() if location_match.groups() else location_match.group(0)
                break
        
        # Tattoo size
        size_match = re.search(r'(?:size|dimensions)[:\s]*([0-9x\s"\']{2,20})', text, re.IGNORECASE)
        if size_match:
            data['tattoo_size'] = size_match.group(1).strip()
        
        # Design description
        design_match = re.search(r'(?:design|description|artwork)[:\s]*([A-Za-z0-9\s]{5,100})', text, re.IGNORECASE)
        if design_match:
            data['design_description'] = design_match.group(1).strip()
        
        # Health information
        allergy_match = re.search(r'(?:allergies|allergic)[:\s]*([A-Za-z\s,]{2,100})', text, re.IGNORECASE)
        if allergy_match:
            data['allergies'] = allergy_match.group(1).strip()
        
        medication_match = re.search(r'(?:medications|meds|drugs)[:\s]*([A-Za-z\s,]{2,100})', text, re.IGNORECASE)
        if medication_match:
            data['medications'] = medication_match.group(1).strip()
        
        # Pricing information
        price_match = re.search(r'\$(\d{1,6}(?:\.\d{2})?)', text)
        if price_match:
            data['pricing'] = float(price_match.group(1))
        
        # Session date
        date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text)
        if date_match:
            data['session_date'] = date_match.group(1)
        
        return data
    
    def identify_document_type(self, filename, text):
        """Identify the type of tattoo document"""
        filename_lower = filename.lower()
        text_lower = text.lower()
        
        if 'consent' in filename_lower or 'consent' in text_lower:
            return 'consent_form'
        elif 'aftercare' in filename_lower or 'aftercare' in text_lower:
            return 'aftercare_instructions'
        elif 'health' in filename_lower or 'medical' in text_lower:
            return 'health_questionnaire'
        elif 'contract' in filename_lower or 'agreement' in text_lower:
            return 'design_contract'
        elif 'release' in filename_lower or 'photo' in text_lower:
            return 'photo_release'
        else:
            return 'general_document'
    
    def calculate_confidence(self, extracted_data):
        """Calculate confidence score based on extracted fields"""
        total_fields = len(self.extraction_fields)
        extracted_fields = len([k for k in extracted_data.keys() if k in self.extraction_fields and extracted_data[k]])
        return round(extracted_fields / total_fields, 3)

# Initialize document processor
doc_processor = TattooDocumentProcessor()

@app.route('/')
def index():
    """Main dashboard for tattoo parlors"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('index.html', 
                         app_name=INDUSTRY_CONFIG['name'],
                         industry=INDUSTRY_CONFIG['industry'],
                         brand_color=INDUSTRY_CONFIG['brand_color'],
                         document_types=INDUSTRY_CONFIG['document_types'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User authentication"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = db_manager.get_connection()
        if conn:
            try:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute(
                    "SELECT id, username, password_hash, role, parlor_name FROM users WHERE username = %s AND is_active = TRUE",
                    (username,)
                )
                user = cursor.fetchone()
                
                if user and user['password_hash'] == hash_password(password):
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['role'] = user['role']
                    session['parlor_name'] = user['parlor_name']
                    
                    # Update last login
                    cursor.execute(
                        "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s",
                        (user['id'],)
                    )
                    conn.commit()
                    
                    flash('Login successful!', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Invalid username or password', 'error')
                    
                cursor.close()
                conn.close()
                
            except psycopg2.Error as e:
                app.logger.error(f"Login error: {e}")
                flash('Login system error', 'error')
    
    return render_template('auth.html', 
                         app_name=INDUSTRY_CONFIG['name'],
                         brand_color=INDUSTRY_CONFIG['brand_color'])

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/api/process', methods=['POST'])
@login_required
def api_process_document():
    """API endpoint for document processing"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'success': False, 'error': 'Only PDF files are supported'})
    
    try:
        # Process the document
        file_content = file.read()
        result = doc_processor.process_document(file_content, file.filename)
        
        if result['success']:
            # Save to database
            conn = db_manager.get_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO document_processing 
                        (user_id, document_type, filename, extracted_data, 
                         processing_time, processing_method, confidence_score)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        session['user_id'],
                        result['extracted_data'].get('document_type', 'unknown'),
                        file.filename,
                        json.dumps(result['extracted_data']),
                        result['processing_time'],
                        result['processing_method'],
                        result['confidence_score']
                    ))
                    
                    processing_id = cursor.fetchone()[0]
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    result['processing_id'] = processing_id
                    
                except psycopg2.Error as e:
                    app.logger.error(f"Database save error: {e}")
        
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"API processing error: {e}")
        return jsonify({'success': False, 'error': 'Processing failed'})

@app.route('/api/status')
def api_status():
    """System status endpoint"""
    return jsonify({
        'status': 'operational',
        'industry': INDUSTRY_CONFIG['industry'],
        'app_name': INDUSTRY_CONFIG['name'],
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # Initialize database on startup
    if db_manager.init_tables():
        app.logger.info("Database initialized successfully")
    else:
        app.logger.error("Database initialization failed")
    
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
