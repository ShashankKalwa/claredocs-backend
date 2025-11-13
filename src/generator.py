import io
import logging
import os
from pdf2image import convert_from_bytes
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
OCR_MODEL = "gemini-2.5-pro"

def perform_gemini_ocr(pdf_bytes: bytes) -> dict:
    """
    Perform OCR on each PDF page using Gemini 2.5 Pro Vision.
    Returns full extracted text with page markers and total page count.
    """
    try:
        pages = convert_from_bytes(pdf_bytes, dpi=200)
        full_text = ""
        model = genai.GenerativeModel(OCR_MODEL)

        for i, page in enumerate(pages):
            # Convert each PDF page to image bytes
            buffer = io.BytesIO()
            page.save(buffer, format="JPEG", quality=70)
            image_data = buffer.getvalue()

            prompt = f"Extract *all visible text* from page {i+1} of this document. Keep reading order and punctuation."

            response = model.generate_content(
                [prompt, {"mime_type": "image/jpeg", "data": image_data}],
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 1500
                },
            )

            page_text = response.text.strip() if response.text else ""
            full_text += f"\n\n--- PAGE {i+1} ---\n{page_text}"

        return {
            "text": full_text.strip(),
            "pages": len(pages)
        }

    except Exception as e:
        logging.error(f"Gemini OCR Error: {e}")
        return {"text": "", "pages": 0}
