import io
import base64
import logging
from pdf2image import convert_from_bytes
import google.generativeai as genai
import os

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
OCR_MODEL = "gemini-2.5-pro"

def perform_gemini_ocr(pdf_bytes: bytes) -> dict:
    """Perform OCR on each PDF page using Gemini 2.5 Pro Vision safely."""
    try:
        pages = convert_from_bytes(pdf_bytes, dpi=200)
        full_text = ""

        for i, page in enumerate(pages):
            buffer = io.BytesIO()
            page.save(buffer, format="JPEG", quality=70)
            buffer.seek(0)

            model = genai.GenerativeModel(OCR_MODEL)

            try:
                response = model.generate_content(
                    [
                        "Extract all visible and readable text from this page clearly and accurately.",
                        {"mime_type": "image/jpeg", "data": buffer.getvalue()},
                    ],
                    request_options={"timeout": 180},
                )

                # ✅ Safely check if the response contains text
                if response and getattr(response, "candidates", None):
                    candidate = response.candidates[0]
                    finish_reason = getattr(candidate, "finish_reason", None)

                    # Only add if Gemini actually produced text
                    if (
                        finish_reason == 1  # NORMAL
                        and candidate.content
                        and candidate.content.parts
                    ):
                        page_text = "".join(
                            [part.text for part in candidate.content.parts if hasattr(part, "text")]
                        ).strip()
                    else:
                        page_text = ""
                else:
                    page_text = ""

            except Exception as inner_e:
                logging.error(f"Gemini OCR Page {i+1} Error: {inner_e}")
                page_text = ""

            if not page_text:
                logging.warning(f"⚠️ No text extracted from page {i+1} (possibly image-only or empty).")

            full_text += f"\n\n--- PAGE {i+1} ---\n{page_text}"

        return {
            "text": full_text.strip(),
            "pages": len(pages)
        }

    except Exception as e:
        logging.error(f"Gemini OCR Error: {e}")
        return {"text": "", "pages": 0}
