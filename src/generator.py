import io
import logging
import base64
from pdf2image import convert_from_bytes
import google.generativeai as genai
import os

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
OCR_MODEL = "gemini-3.0-pro"      # Vision-capable

def perform_gemini_ocr(pdf_bytes: bytes) -> dict:
    """Extract text from each PDF page using Gemini 3.0 Pro Vision."""
    try:
        pages = convert_from_bytes(pdf_bytes, dpi=200)
        full_text = ""

        for i, page in enumerate(pages):
            buffer = io.BytesIO()
            page.save(buffer, "JPEG", quality=70)
            img_data = buffer.getvalue()

            model = genai.GenerativeModel(OCR_MODEL)

            try:
                response = model.generate_content(
                    [
                        "Extract all visible text from this page clearly.",
                        {"mime_type": "image/jpeg", "data": img_data}
                    ],
                    request_options={"timeout": 180}
                )

                # Safe extraction
                if response and response.candidates:
                    candidate = response.candidates[0]
                    if candidate.content and candidate.content.parts:
                        page_text = "".join(
                            part.text for part in candidate.content.parts
                            if hasattr(part, "text")
                        ).strip()
                    else:
                        page_text = ""
                else:
                    page_text = ""

            except Exception as e:
                logging.error(f"OCR error on page {i+1}: {e}")
                page_text = ""

            if not page_text:
                logging.warning(f"No text extracted from page {i+1}")

            full_text += f"\n\n--- PAGE {i+1} ---\n{page_text}"

        return {
            "text": full_text.strip(),
            "pages": len(pages)
        }

    except Exception as e:
        logging.error(f"Gemini OCR error: {e}")
        return {"text": "", "pages": 0}
