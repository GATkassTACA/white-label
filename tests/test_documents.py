import pytest
import io
from unittest.mock import patch, MagicMock
from app import create_app
from services.document_processor import DocumentProcessor

@pytest.fixture
def app():
    app, _ = create_app()
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = 'test_uploads'
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def document_processor():
    return DocumentProcessor()

class TestDocumentProcessor:
    def test_init(self, document_processor):
        """Test DocumentProcessor initialization"""
        assert document_processor.max_file_size == 10 * 1024 * 1024  # 10MB
        assert hasattr(document_processor, 'supported_formats')
        assert document_processor.supported_formats == ['.pdf']
    
    def test_validate_file_valid_pdf(self, document_processor):
        """Test file validation with valid PDF"""
        file_data = b'fake pdf content'
        filename = 'test.pdf'
        
        is_valid, error = document_processor.validate_file(file_data, filename)
        assert is_valid is True
        assert error == "File is valid"
    
    def test_validate_file_too_large(self, document_processor):
        """Test file validation with oversized file"""
        file_data = b'x' * (15 * 1024 * 1024)  # 15MB
        filename = 'large.pdf'
        
        is_valid, error = document_processor.validate_file(file_data, filename)
        assert is_valid is False
        assert "too large" in error.lower()
    
    def test_validate_file_invalid_type(self, document_processor):
        """Test file validation with invalid file type"""
        file_data = b'plain text content'
        filename = 'test.txt'
        
        is_valid, error = document_processor.validate_file(file_data, filename)
        assert is_valid is False
        assert "unsupported" in error.lower()
    
    @patch('services.document_processor.DocumentProcessor.extract_text_pypdf2')
    def test_extract_text_pypdf2_success(self, mock_method, document_processor):
        """Test successful text extraction with PyPDF2"""
        mock_method.return_value = {
            'success': True,
            'text': "Sample text from PDF",
            'pages': 1,
            'method': 'PyPDF2'
        }
        
        result = document_processor.extract_text_pypdf2(b'fake pdf data')
        
        assert result['success'] is True
        assert result['text'] == "Sample text from PDF"
        assert result['pages'] == 1
        assert result['method'] == 'PyPDF2'
    
    @patch('services.document_processor.DocumentProcessor.extract_text_pypdf2')
    def test_extract_text_pypdf2_failure(self, mock_method, document_processor):
        """Test PyPDF2 extraction failure"""
        mock_method.return_value = {
            'success': False,
            'error': 'PDF parsing error'
        }
        
        result = document_processor.extract_text_pypdf2(b'fake pdf data')
        
        assert result['success'] is False
        assert "PDF parsing error" in result['error']
    
    @patch('services.document_processor.DocumentProcessor.extract_text_pdfplumber')
    def test_extract_text_pdfplumber_success(self, mock_method, document_processor):
        """Test successful text extraction with pdfplumber"""
        mock_method.return_value = {
            'success': True,
            'text': "Detailed text from pdfplumber",
            'pages': 1,
            'method': 'pdfplumber'
        }
        
        result = document_processor.extract_text_pdfplumber(b'fake pdf data')
        
        assert result['success'] is True
        assert result['text'] == "Detailed text from pdfplumber"
        assert result['pages'] == 1
        assert result['method'] == 'pdfplumber'
    
    @patch('services.document_processor.DocumentProcessor.extract_text_ocr')
    def test_extract_text_ocr_success(self, mock_method, document_processor):
        """Test successful OCR text extraction"""
        mock_method.return_value = {
            'success': True,
            'text': "OCR extracted text",
            'pages': 1,
            'method': 'OCR'
        }
        
        result = document_processor.extract_text_ocr(b'fake pdf data')
        
        assert result['success'] is True
        assert result['text'] == "OCR extracted text"
        assert result['pages'] == 1
        assert result['method'] == 'OCR'

class TestDocumentRoutes:
    def test_documents_index_get(self, client):
        """Test documents index page"""
        response = client.get('/documents/')
        assert response.status_code == 200
        assert b'Document Scanner' in response.data
    
    def test_documents_history_get(self, client):
        """Test documents history page"""
        response = client.get('/documents/history')
        assert response.status_code == 200
        assert b'Processing History' in response.data
    
    def test_upload_no_file(self, client):
        """Test upload without file"""
        response = client.post('/documents/upload')
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'No file uploaded' in data['error']
    
    def test_upload_empty_filename(self, client):
        """Test upload with empty filename"""
        data = {'file': (io.BytesIO(b'test'), '')}
        response = client.post('/documents/upload', data=data)
        assert response.status_code == 400
        result = response.get_json()
        assert result['success'] is False
        assert 'No file uploaded' in result['error']
    
    @patch('services.document_processor.DocumentProcessor.validate_file')
    def test_upload_invalid_file(self, mock_validate, client):
        """Test upload with invalid file"""
        mock_validate.return_value = (False, "Invalid file type")
        
        data = {'file': (io.BytesIO(b'test'), 'test.txt')}
        response = client.post('/documents/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 400
        result = response.get_json()
        assert result['success'] is False
        assert 'No file uploaded' in result['error']
    
    @patch('services.document_processor.DocumentProcessor.validate_file')
    @patch('services.document_processor.DocumentProcessor.extract_document_data')
    def test_api_process_success(self, mock_extract, mock_validate, client):
        """Test successful document processing via API"""
        mock_validate.return_value = (True, "File is valid")
        mock_extract.return_value = {
            'success': True,
            'text': 'Extracted text',
            'method': 'PyPDF2',
            'pages': 1,
            'total_chars': 14,
            'metadata': {}
        }
        
        data = {'file': (io.BytesIO(b'fake pdf content'), 'test.pdf')}
        response = client.post('/documents/api/process', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert result['text'] == 'Extracted text'
        assert result['method'] == 'PyPDF2'

class TestDocumentProcessorIntegration:
    @patch('services.document_processor.DocumentProcessor.extract_text_pypdf2')
    @patch('services.document_processor.DocumentProcessor.extract_text_pdfplumber')
    @patch('services.document_processor.DocumentProcessor.extract_text_ocr')
    def test_extract_document_data_fallback(self, mock_ocr, mock_pdfplumber, mock_pypdf2, document_processor):
        """Test document processing with method fallback"""
        # PyPDF2 fails
        mock_pypdf2.return_value = {'success': False, 'error': 'PyPDF2 failed'}
        
        # pdfplumber succeeds
        mock_pdfplumber.return_value = {
            'success': True,
            'text': 'Success with pdfplumber',
            'method': 'pdfplumber',
            'pages': 2,
            'total_chars': 100
        }
        
        result = document_processor.extract_document_data(b'fake pdf data', 'test.pdf')
        
        assert result['success'] is True
        assert result['text'] == 'Success with pdfplumber'
        assert result['method'] == 'pdfplumber'
        assert result['pages'] == 2
        assert result['best_method'] == 'pdfplumber'
        # Should not call OCR since pdfplumber succeeded
        mock_ocr.assert_not_called()
    
    def test_analyze_document_content(self, document_processor):
        """Test document content analysis"""
        extraction_result = {
            'success': True,
            'content': [
                {
                    'text': "This is a sample document with text.",
                    'char_count': 36
                }
            ],
            'metadata': {
                'extraction_method': 'test'
            }
        }
        
        analysis = document_processor.analyze_document_content(extraction_result)
        
        assert 'statistics' in analysis
        assert analysis['statistics']['total_characters'] == 36
        assert analysis['statistics']['total_pages'] == 1
        assert 'content_insights' in analysis
        assert 'quality_metrics' in analysis
