"""
Document processing service for PDF data extraction
Supports text extraction, OCR, and metadata extraction
"""

import os
import io
import json
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

try:
    import PyPDF2
    import pdfplumber
    from PIL import Image
    import pytesseract
    from pdf2image import convert_from_bytes
except ImportError as e:
    logging.warning(f"PDF processing libraries not available: {e}")
    PyPDF2 = pdfplumber = pytesseract = None

class DocumentProcessor:
    """Service for processing and extracting data from PDF documents"""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        
    def is_supported_format(self, filename: str) -> bool:
        """Check if file format is supported"""
        return any(filename.lower().endswith(fmt) for fmt in self.supported_formats)
    
    def validate_file(self, file_data: bytes, filename: str) -> Tuple[bool, str]:
        """Validate uploaded file"""
        if not self.is_supported_format(filename):
            return False, f"Unsupported format. Supported: {', '.join(self.supported_formats)}"
        
        if len(file_data) > self.max_file_size:
            return False, f"File too large. Max size: {self.max_file_size // (1024*1024)}MB"
        
        return True, "File is valid"
    
    def extract_text_pypdf2(self, file_data: bytes) -> Dict:
        """Extract text using PyPDF2 (fast, basic extraction)"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_data))
            
            text_content = []
            metadata = {
                'num_pages': len(pdf_reader.pages),
                'extraction_method': 'PyPDF2',
                'timestamp': datetime.now().isoformat()
            }
            
            # Extract document metadata
            if pdf_reader.metadata:
                metadata.update({
                    'title': pdf_reader.metadata.get('/Title', ''),
                    'author': pdf_reader.metadata.get('/Author', ''),
                    'subject': pdf_reader.metadata.get('/Subject', ''),
                    'creator': pdf_reader.metadata.get('/Creator', ''),
                    'creation_date': str(pdf_reader.metadata.get('/CreationDate', ''))
                })
            
            # Extract text from each page
            for page_num, page in enumerate(pdf_reader.pages, 1):
                try:
                    page_text = page.extract_text()
                    text_content.append({
                        'page': page_num,
                        'text': page_text.strip(),
                        'char_count': len(page_text)
                    })
                except Exception as e:
                    text_content.append({
                        'page': page_num,
                        'text': '',
                        'error': str(e)
                    })
            
            return {
                'success': True,
                'metadata': metadata,
                'content': text_content,
                'total_chars': sum(page.get('char_count', 0) for page in text_content)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"PyPDF2 extraction failed: {str(e)}"
            }
    
    def extract_text_pdfplumber(self, file_data: bytes) -> Dict:
        """Extract text using pdfplumber (more accurate, slower)"""
        try:
            with pdfplumber.open(io.BytesIO(file_data)) as pdf:
                text_content = []
                tables = []
                
                metadata = {
                    'num_pages': len(pdf.pages),
                    'extraction_method': 'pdfplumber',
                    'timestamp': datetime.now().isoformat()
                }
                
                # Extract document metadata
                if pdf.metadata:
                    metadata.update({
                        'title': pdf.metadata.get('Title', ''),
                        'author': pdf.metadata.get('Author', ''),
                        'subject': pdf.metadata.get('Subject', ''),
                        'creator': pdf.metadata.get('Creator', ''),
                        'creation_date': str(pdf.metadata.get('CreationDate', ''))
                    })
                
                # Process each page
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        # Extract text
                        page_text = page.extract_text() or ""
                        
                        # Extract tables
                        page_tables = page.extract_tables()
                        
                        text_content.append({
                            'page': page_num,
                            'text': page_text.strip(),
                            'char_count': len(page_text),
                            'table_count': len(page_tables)
                        })
                        
                        # Store table data
                        for table_idx, table in enumerate(page_tables):
                            tables.append({
                                'page': page_num,
                                'table_index': table_idx,
                                'rows': len(table),
                                'columns': len(table[0]) if table else 0,
                                'data': table
                            })
                    
                    except Exception as e:
                        text_content.append({
                            'page': page_num,
                            'text': '',
                            'error': str(e)
                        })
                
                return {
                    'success': True,
                    'metadata': metadata,
                    'content': text_content,
                    'tables': tables,
                    'total_chars': sum(page.get('char_count', 0) for page in text_content),
                    'total_tables': len(tables)
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"pdfplumber extraction failed: {str(e)}"
            }
    
    def extract_text_ocr(self, file_data: bytes) -> Dict:
        """Extract text using OCR (for scanned PDFs)"""
        try:
            # Convert PDF to images
            images = convert_from_bytes(file_data)
            
            text_content = []
            metadata = {
                'num_pages': len(images),
                'extraction_method': 'OCR (pytesseract)',
                'timestamp': datetime.now().isoformat()
            }
            
            for page_num, image in enumerate(images, 1):
                try:
                    # Perform OCR on the image
                    page_text = pytesseract.image_to_string(image)
                    
                    # Get OCR confidence data
                    ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                    confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                    
                    text_content.append({
                        'page': page_num,
                        'text': page_text.strip(),
                        'char_count': len(page_text),
                        'ocr_confidence': round(avg_confidence, 2),
                        'word_count': len([word for word in ocr_data['text'] if word.strip()])
                    })
                    
                except Exception as e:
                    text_content.append({
                        'page': page_num,
                        'text': '',
                        'error': str(e)
                    })
            
            return {
                'success': True,
                'metadata': metadata,
                'content': text_content,
                'total_chars': sum(page.get('char_count', 0) for page in text_content),
                'avg_confidence': sum(page.get('ocr_confidence', 0) for page in text_content) / len(text_content)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"OCR extraction failed: {str(e)}"
            }
    
    def extract_document_data(self, file_data: bytes, filename: str, method: str = 'auto') -> Dict:
        """
        Main method to extract data from PDF document
        
        Args:
            file_data: PDF file content as bytes
            filename: Original filename
            method: Extraction method ('auto', 'pypdf2', 'pdfplumber', 'ocr')
        """
        # Validate file
        is_valid, validation_message = self.validate_file(file_data, filename)
        if not is_valid:
            return {
                'success': False,
                'error': validation_message
            }
        
        results = {
            'filename': filename,
            'file_size': len(file_data),
            'extraction_attempts': []
        }
        
        # Try different extraction methods based on the specified method
        if method == 'auto':
            # Try methods in order of preference
            methods_to_try = ['pdfplumber', 'pypdf2', 'ocr']
        elif method in ['pypdf2', 'pdfplumber', 'ocr']:
            methods_to_try = [method]
        else:
            return {
                'success': False,
                'error': f"Unknown extraction method: {method}"
            }
        
        best_result = None
        
        for extract_method in methods_to_try:
            try:
                if extract_method == 'pypdf2' and PyPDF2:
                    result = self.extract_text_pypdf2(file_data)
                elif extract_method == 'pdfplumber' and pdfplumber:
                    result = self.extract_text_pdfplumber(file_data)
                elif extract_method == 'ocr' and pytesseract:
                    result = self.extract_text_ocr(file_data)
                else:
                    continue
                
                results['extraction_attempts'].append({
                    'method': extract_method,
                    'success': result['success'],
                    'error': result.get('error', None)
                })
                
                if result['success']:
                    # Check if this result is better than previous ones
                    total_chars = result.get('total_chars', 0)
                    if best_result is None or total_chars > best_result.get('total_chars', 0):
                        best_result = result
                        results['best_method'] = extract_method
                    
                    # If pdfplumber works well, use it (it's usually the best)
                    if extract_method == 'pdfplumber' and total_chars > 0:
                        break
                        
            except Exception as e:
                results['extraction_attempts'].append({
                    'method': extract_method,
                    'success': False,
                    'error': str(e)
                })
        
        if best_result:
            results.update(best_result)
            return results
        else:
            return {
                'success': False,
                'error': 'All extraction methods failed',
                'extraction_attempts': results['extraction_attempts']
            }
    
    def analyze_document_content(self, extraction_result: Dict) -> Dict:
        """Analyze extracted document content for insights"""
        if not extraction_result.get('success'):
            return {'error': 'No successful extraction to analyze'}
        
        content = extraction_result.get('content', [])
        
        # Basic statistics
        total_pages = len(content)
        total_chars = sum(page.get('char_count', 0) for page in content)
        total_words = 0
        
        # Content analysis
        all_text = ""
        for page in content:
            page_text = page.get('text', '')
            all_text += page_text + " "
            total_words += len(page_text.split())
        
        # Simple keyword extraction (most common words)
        words = all_text.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Only words longer than 3 chars
                word_freq[word] = word_freq.get(word, 0) + 1
        
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        analysis = {
            'statistics': {
                'total_pages': total_pages,
                'total_characters': total_chars,
                'total_words': total_words,
                'avg_chars_per_page': total_chars / total_pages if total_pages > 0 else 0,
                'avg_words_per_page': total_words / total_pages if total_pages > 0 else 0
            },
            'content_insights': {
                'top_keywords': top_keywords,
                'document_length': 'short' if total_words < 500 else 'medium' if total_words < 2000 else 'long',
                'has_tables': extraction_result.get('total_tables', 0) > 0,
                'table_count': extraction_result.get('total_tables', 0)
            },
            'quality_metrics': {
                'extraction_method': extraction_result.get('metadata', {}).get('extraction_method', 'unknown'),
                'avg_confidence': extraction_result.get('avg_confidence'),
                'pages_with_errors': len([p for p in content if 'error' in p])
            }
        }
        
        return analysis
