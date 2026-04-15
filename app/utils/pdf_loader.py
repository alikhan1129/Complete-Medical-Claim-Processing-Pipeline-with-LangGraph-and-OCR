import pdfplumber
import logging
import pytesseract
from pdf2image import convert_from_path
from typing import List, Dict
import os

logger = logging.getLogger(__name__)

# Set Tesseract executable path - Handle both Windows and Linux (Render)
windows_tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if os.path.exists(windows_tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = windows_tesseract_path
else:
    # On Linux/Render, Tesseract is usually in the PATH after apt-get install
    pytesseract.pytesseract.tesseract_cmd = 'tesseract'

def extract_text_from_pdf(file_path: str) -> List[Dict[str, any]]:
    """
    Extracts text from each page of the PDF.
    Tries normal extraction first, falls back to OCR if no text is found.
    """
    pages_text = []
    try:
        # 1. Try normal text extraction
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    pages_text.append({
                        "page_number": i + 1,
                        "text": text
                    })
                else:
                    logger.warning(f"No text on page {i + 1}. Attempting OCR...")
        
        # 2. If no text was found on any page, or some pages were empty, use OCR
        if not pages_text or len(pages_text) < len(pdf.pages):
            logger.info("Some pages are empty. Using OCR fallback for missing pages...")
            
            # Convert PDF to images (requires poppler installed)
            images = convert_from_path(file_path)
            
            # Map of already extracted pages
            existing_pages = {p["page_number"] for p in pages_text}
            
            for i, image in enumerate(images):
                page_num = i + 1
                if page_num not in existing_pages:
                    logger.info(f"Running OCR on page {page_num}...")
                    ocr_text = pytesseract.image_to_string(image)
                    if ocr_text.strip():
                        pages_text.append({
                            "page_number": page_num,
                            "text": ocr_text
                        })
                    else:
                        logger.warning(f"OCR also failed to extract text from page {page_num}")

        # Sort pages to keep them in order
        pages_text.sort(key=lambda x: x["page_number"])

    except Exception as e:
        logger.error(f"Error extracting text from PDF (with OCR): {str(e)}")
        raise e
        
    return pages_text
