import io
import base64
from pypdf import PdfReader
from pdf2image import convert_from_bytes
from PIL import Image
from openai import OpenAI
import logging
from .utils import get_env_variable

class DocumentProcessor:
    def __init__(self):
        """Initialize the document processor with OCR capabilities"""
        # Initialize OpenAI client for GPT-4o OCR
        api_key = get_env_variable("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.ocr_model = "gpt-4o"
        self.used_ocr_for_extraction = False
    
    def extract_text_from_pdf(self, file_bytes):
        """
        Extract text from a PDF file
        
        Args:
            file_bytes (bytes): The PDF file as bytes
            
        Returns:
            str: Extracted text from the PDF
        """
        # Reset OCR flag at the start of each extraction
        self.used_ocr_for_extraction = False
        
        pdf_file = io.BytesIO(file_bytes)
        pdf_reader = PdfReader(pdf_file)
        text = ""
        
        # First try direct text extraction
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
        
        # If no text was extracted, try OCR with GPT-4o
        if not text.strip():
            logging.info("No text extracted directly from PDF. Trying OCR...")
            self.used_ocr_for_extraction = True
            try:
                text = self._perform_gpt4o_ocr(file_bytes)
                if text.strip():
                    logging.info("Successfully extracted text using GPT-4o OCR")
            except Exception as e:
                logging.error(f"Error with GPT-4o OCR: {str(e)}.")
                text = ""
            
        return text
    
    def _perform_gpt4o_ocr(self, file_bytes):
        """
        Perform OCR using GPT-4o on a PDF file
        
        Args:
            file_bytes (bytes): The PDF file as bytes
            
        Returns:
            str: Extracted text from OCR
        """
        try:
            images = convert_from_bytes(file_bytes)
            full_text = ""
            
            for i, img in enumerate(images):
                # Convert PIL Image to base64
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                base64_image = base64.b64encode(img_byte_arr).decode('utf-8')
                
                # Call GPT-4o for OCR
                response = self.client.chat.completions.create(
                    model=self.ocr_model,
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are an OCR assistant. Extract ALL text from the image, preserving layout where possible. Include all text visible in the image, including headers, footers, tables, and any text in different languages. For legal documents, pay special attention to dates, names, and legal terms."
                        },
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": f"Extract all text from this document image (page {i+1}). Preserve the original formatting as much as possible."},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                            ]
                        }
                    ],
                    max_tokens=1500
                )
                
                page_text = response.choices[0].message.content
                full_text += page_text + "\n\n"
                
            return full_text
            
        except Exception as e:
            logging.error(f"Error in GPT-4o OCR: {str(e)}")
            return ""