import os
import uuid
from werkzeug.utils import secure_filename
from app_config import settings


class FileProcessor:
    def __init__(self):
        self.upload_folder = settings.UPLOAD_FOLDER
        self.allowed_extensions = settings.ALLOWED_EXTENSIONS
    
    def allowed_file(self, filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def save_file(self, file, session_id):
        """Save uploaded file and return file path"""
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add session ID to filename to avoid conflicts
            name, ext = os.path.splitext(filename)
            filename = f"{session_id}_{name}{ext}"
            
            file_path = os.path.join(self.upload_folder, filename)
            file.save(file_path)
            return file_path
        else:
            raise ValueError("Invalid file type")
    
    def extract_text(self, file_path):
        """Extract text from uploaded file"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.txt':
            return self._extract_from_txt(file_path)
        elif file_ext == '.pdf':
            return self._extract_from_pdf(file_path)
        elif file_ext in ['.doc', '.docx']:
            return self._extract_from_doc(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    def _extract_from_txt(self, file_path):
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
    
    def _extract_from_pdf(self, file_path):
        """Extract text from PDF file"""
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except ImportError:
            # Fallback to basic text extraction
            return "PDF text extraction requires PyPDF2. Please install it with: pip install PyPDF2"
        except Exception as e:
            return f"Error extracting PDF text: {str(e)}"
    
    def _extract_from_doc(self, file_path):
        """Extract text from DOC/DOCX file"""
        try:
            import docx
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except ImportError:
            return "DOC/DOCX text extraction requires python-docx. Please install it with: pip install python-docx"
        except Exception as e:
            return f"Error extracting DOC text: {str(e)}"
