import re
import os
from typing import List
import PyPDF2
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class PDFPreprocessor:
    """
    Handles extraction and cleaning of text from NCERT PDFs
    """
    
    def __init__(self, pdf_dir: str = "data/raw_pdfs"):
        self.pdf_dir = pdf_dir
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract raw text from a PDF file"""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                logger.info(f"Extracting text from {os.path.basename(pdf_path)} ({num_pages} pages)")
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            
            return text
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers
        text = re.sub(r'\b\d{1,3}\b\s*(?:NCERT|Science|Mathematics|English)?', '', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-\'\"]+', '', text)
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
        
        # Remove multiple spaces
        text = ' '.join(text.split())
        
        return text.strip()
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """
        Split text into overlapping chunks for better context preservation
        """
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk.strip()) > 50:  # Minimum chunk size
                chunks.append(chunk)
        
        return chunks
    
    def process_all_pdfs(self, output_dir: str = "data/processed_texts") -> dict:
        """
        Process all PDFs in the raw_pdfs directory
        Returns a dictionary mapping filenames to their processed chunks
        """
        os.makedirs(output_dir, exist_ok=True)
        
        if not os.path.exists(self.pdf_dir):
            logger.error(f"PDF directory not found: {self.pdf_dir}")
            return {}
        
        processed_data = {}
        pdf_files = [f for f in os.listdir(self.pdf_dir) if f.endswith('.pdf')]
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {self.pdf_dir}")
            return {}
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.pdf_dir, pdf_file)
            
            # Extract text
            raw_text = self.extract_text_from_pdf(pdf_path)
            
            if not raw_text:
                continue
            
            # Clean text
            clean = self.clean_text(raw_text)
            
            # Chunk text
            chunks = self.chunk_text(clean)
            
            # Save processed text
            output_file = os.path.join(output_dir, f"{os.path.splitext(pdf_file)[0]}.txt")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n\n---CHUNK---\n\n'.join(chunks))
            
            processed_data[pdf_file] = chunks
            logger.info(f"Processed {pdf_file}: {len(chunks)} chunks created")
        
        return processed_data

def preprocess_ncert_data(raw_dir='data/raw_pdfs', output_dir='data/processed_texts'):
    """Main preprocessing function"""
    preprocessor = PDFPreprocessor(raw_dir)
    return preprocessor.process_all_pdfs()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    preprocessor = PDFPreprocessor()
    result = preprocessor.process_all_pdfs()
    print(f"Processed {len(result)} PDF files")
