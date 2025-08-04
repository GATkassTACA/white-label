"""
PharmAssist PDF Processing Services
Layer 3: Core PDF processing functionality with multiple methods
"""
import io
import os
import re
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# PDF processing libraries
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import pytesseract
    from PIL import Image
    import fitz  # PyMuPDF for image extraction
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Main PDF processing class with multiple extraction methods"""
    
    def __init__(self):
        self.supported_methods = self._check_available_methods()
        logger.info(f"PDF Processor initialized with methods: {list(self.supported_methods.keys())}")
    
    def _check_available_methods(self) -> Dict[str, bool]:
        """Check which processing methods are available"""
        return {
            'pypdf2': PYPDF2_AVAILABLE,
            'pdfplumber': PDFPLUMBER_AVAILABLE,
            'ocr': OCR_AVAILABLE
        }
    
    def process_pdf(self, file_content: bytes, method: str = 'auto', filename: str = '') -> Dict:
        """
        Main processing function that routes to appropriate method
        
        Args:
            file_content: PDF file content as bytes
            method: Processing method ('auto', 'pypdf2', 'pdfplumber', 'ocr')
            filename: Original filename for reference
            
        Returns:
            Dict with processing results
        """
        try:
            logger.info(f"Processing PDF: {filename} with method: {method}")
            
            if method == 'auto':
                method = self._detect_best_method(file_content)
                logger.info(f"Auto-detected method: {method}")
            
            # Route to appropriate processor
            if method == 'pypdf2' and self.supported_methods['pypdf2']:
                return self._process_with_pypdf2(file_content, filename)
            elif method == 'pdfplumber' and self.supported_methods['pdfplumber']:
                return self._process_with_pdfplumber(file_content, filename)
            elif method == 'ocr' and self.supported_methods['ocr']:
                return self._process_with_ocr(file_content, filename)
            else:
                # Fallback to basic text extraction
                return self._process_basic(file_content, filename)
                
        except Exception as e:
            logger.error(f"Error processing PDF {filename}: {str(e)}")
            return {
                'success': False,
                'error': f"Processing failed: {str(e)}",
                'method_used': method
            }
    
    def _detect_best_method(self, file_content: bytes) -> str:
        """Automatically detect the best processing method for the PDF"""
        try:
            # Try to extract some text with PyPDF2 first (fastest)
            if PYPDF2_AVAILABLE:
                pdf_file = io.BytesIO(file_content)
                reader = PyPDF2.PdfReader(pdf_file)
                
                if len(reader.pages) > 0:
                    text = reader.pages[0].extract_text()
                    if len(text.strip()) > 50:  # Good amount of extractable text
                        return 'pypdf2'
                    elif len(text.strip()) > 10:  # Some text, try pdfplumber for tables
                        return 'pdfplumber' if PDFPLUMBER_AVAILABLE else 'pypdf2'
                    else:
                        return 'ocr' if OCR_AVAILABLE else 'pdfplumber'
            
            # Fallback order
            if PDFPLUMBER_AVAILABLE:
                return 'pdfplumber'
            elif OCR_AVAILABLE:
                return 'ocr'
            else:
                return 'pypdf2'
                
        except Exception as e:
            logger.warning(f"Method detection failed: {e}, defaulting to pdfplumber")
            return 'pdfplumber' if PDFPLUMBER_AVAILABLE else 'pypdf2'
    
    def _process_with_pypdf2(self, file_content: bytes, filename: str) -> Dict:
        """Process PDF using PyPDF2 for text extraction"""
        try:
            pdf_file = io.BytesIO(file_content)
            reader = PyPDF2.PdfReader(pdf_file)
            
            extracted_text = ""
            pages_processed = len(reader.pages)
            
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                extracted_text += f"\n--- Page {page_num + 1} ---\n{text}\n"
            
            medications = self._extract_medications(extracted_text)
            caretend_output = self._convert_to_caretend(medications, filename)
            
            return {
                'success': True,
                'method_used': 'PyPDF2 Text Extraction',
                'pages_processed': pages_processed,
                'extracted_text': extracted_text,
                'medications_found': medications,
                'medications_count': len(medications),
                'caretend_output': caretend_output,
                'filename': filename
            }
            
        except Exception as e:
            logger.error(f"PyPDF2 processing failed: {e}")
            raise
    
    def _process_with_pdfplumber(self, file_content: bytes, filename: str) -> Dict:
        """Process PDF using pdfplumber for table extraction"""
        try:
            pdf_file = io.BytesIO(file_content)
            extracted_text = ""
            tables = []
            pages_processed = 0
            
            with pdfplumber.open(pdf_file) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    pages_processed += 1
                    
                    # Extract text
                    text = page.extract_text()
                    if text:
                        extracted_text += f"\n--- Page {page_num + 1} ---\n{text}\n"
                    
                    # Extract tables
                    page_tables = page.extract_tables()
                    if page_tables:
                        for table_num, table in enumerate(page_tables):
                            tables.append({
                                'page': page_num + 1,
                                'table': table_num + 1,
                                'data': table
                            })
            
            medications = self._extract_medications_from_tables(tables) + self._extract_medications(extracted_text)
            caretend_output = self._convert_to_caretend(medications, filename)
            
            return {
                'success': True,
                'method_used': 'PDFplumber Table & Text Extraction',
                'pages_processed': pages_processed,
                'extracted_text': extracted_text,
                'tables_found': len(tables),
                'medications_found': medications,
                'medications_count': len(medications),
                'caretend_output': caretend_output,
                'filename': filename
            }
            
        except Exception as e:
            logger.error(f"PDFplumber processing failed: {e}")
            raise
    
    def _process_with_ocr(self, file_content: bytes, filename: str) -> Dict:
        """Process PDF using OCR for scanned documents"""
        try:
            pdf_file = io.BytesIO(file_content)
            extracted_text = ""
            pages_processed = 0
            
            # Convert PDF to images and OCR each page
            doc = fitz.open(stream=pdf_file, filetype="pdf")
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pages_processed += 1
                
                # Convert page to image
                mat = fitz.Matrix(2.0, 2.0)  # Increase resolution
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                
                # OCR the image
                image = Image.open(io.BytesIO(img_data))
                text = pytesseract.image_to_string(image, config='--psm 6')
                
                extracted_text += f"\n--- Page {page_num + 1} (OCR) ---\n{text}\n"
            
            doc.close()
            
            medications = self._extract_medications(extracted_text)
            caretend_output = self._convert_to_caretend(medications, filename)
            
            return {
                'success': True,
                'method_used': 'OCR Text Recognition',
                'pages_processed': pages_processed,
                'extracted_text': extracted_text,
                'medications_found': medications,
                'medications_count': len(medications),
                'caretend_output': caretend_output,
                'filename': filename
            }
            
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            raise
    
    def _process_basic(self, file_content: bytes, filename: str) -> Dict:
        """Basic processing when no specialized libraries are available"""
        return {
            'success': True,
            'method_used': 'Basic Processing (Limited functionality)',
            'pages_processed': 1,
            'extracted_text': 'PDF processing libraries not available. Please install PyPDF2, pdfplumber, or pytesseract.',
            'medications_found': [],
            'medications_count': 0,
            'caretend_output': 'Processing requires additional dependencies.',
            'filename': filename
        }
    
    def _extract_medications(self, text: str) -> List[Dict]:
        """Extract medication information from text using pattern matching"""
        medications = []
        
        # Common medication patterns
        patterns = [
            # Generic drug name pattern
            r'(\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(\d+(?:\.\d+)?)\s*(mg|mcg|g|mL|units?)\b',
            # Brand name pattern
            r'(\b[A-Z][A-Z\s]+)\s+(\d+(?:\.\d+)?)\s*(mg|mcg|g|mL|units?)\b',
            # Dosage pattern
            r'(\w+(?:\s+\w+)*)\s+(\d+(?:\.\d+)?)\s*(mg|mcg|g|mL|units?)\s+(?:take|taken?|daily|twice|once)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                medication = {
                    'name': match.group(1).strip(),
                    'dosage': f"{match.group(2)} {match.group(3)}",
                    'strength': match.group(2),
                    'unit': match.group(3)
                }
                
                # Avoid duplicates
                if not any(med['name'].lower() == medication['name'].lower() for med in medications):
                    medications.append(medication)
        
        return medications
    
    def _extract_medications_from_tables(self, tables: List[Dict]) -> List[Dict]:
        """Extract medications from table structures"""
        medications = []
        
        for table_info in tables:
            table = table_info['data']
            if not table or len(table) < 2:
                continue
            
            # Assume first row is headers
            headers = [str(cell).lower() if cell else '' for cell in table[0]]
            
            # Find relevant columns
            name_col = next((i for i, h in enumerate(headers) if 'drug' in h or 'medication' in h or 'name' in h), 0)
            dose_col = next((i for i, h in enumerate(headers) if 'dose' in h or 'strength' in h or 'amount' in h), 1)
            
            for row in table[1:]:
                if len(row) > max(name_col, dose_col):
                    name = str(row[name_col]) if row[name_col] else ''
                    dose = str(row[dose_col]) if row[dose_col] else ''
                    
                    if name and name.lower() not in ['none', 'null', '']:
                        medication = {
                            'name': name.strip(),
                            'dosage': dose.strip(),
                            'source': 'table_extraction'
                        }
                        medications.append(medication)
        
        return medications
    
    def _convert_to_caretend(self, medications: List[Dict], filename: str) -> str:
        """Convert medications to CareTend format"""
        if not medications:
            return "No medications found for CareTend conversion."
        
        caretend_output = f"""CareTend Format Medication List
Source: {filename}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Medications: {len(medications)}

--- MEDICATION LIST ---
"""
        
        for i, med in enumerate(medications, 1):
            caretend_output += f"""
{i}. Medication: {med.get('name', 'Unknown')}
   Dosage: {med.get('dosage', 'Not specified')}
   Status: Active
   Source: PDF Document Processing
"""
        
        caretend_output += f"""
--- END MEDICATION LIST ---

Notes:
- This list was automatically extracted from PDF document
- Please verify all medications and dosages with patient
- Suitable for insurance submission and medical record keeping
- CareTend compatible format
"""
        
        return caretend_output

# Initialize the processor
pdf_processor = PDFProcessor()
