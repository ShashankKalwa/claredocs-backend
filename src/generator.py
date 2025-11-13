import io
import base64
import logging
from pdf2image import convert_from_bytes
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
OCR_MODEL = "gpt-4o"

def perform_gpt4o_ocr(pdf_bytes: bytes) -> dict:
    """Perform OCR on each PDF page using GPT-4o Vision and return text + page count."""
    try:
        pages = convert_from_bytes(pdf_bytes, dpi=200)
        full_text = ""

        for i, page in enumerate(pages):
            buffer = io.BytesIO()
            page.save(buffer, format="JPEG", quality=60)
            img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

            response = client.chat.completions.create(
                model=OCR_MODEL,
                messages=[
                    {"role": "system", "content": "You are an OCR assistant. Extract visible text accurately."},
                    {"role": "user",
                     "content": [
                         {"type": "text", "text": f"Extract text from page {i+1}."},
                         {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                     ]}
                ],
                max_tokens=1500
            )

            page_text = response.choices[0].message.content.strip()
            full_text += f"\n\n--- PAGE {i+1} ---\n{page_text}"

        return {
            "text": full_text.strip(),
            "pages": len(pages)
        }

    except Exception as e:
        logging.error(f"OCR Error: {e}")
        return {"text": "", "pages": 0}
