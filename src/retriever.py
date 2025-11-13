import os
import json
import google.generativeai as genai

# Configure Gemini client
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

ANALYSIS_MODEL = "gemini-2.5-pro"  # ✅ Latest Gemini model

def analyze_with_gemini(text: str) -> dict:
    """
    Uses Gemini 2.5 Pro to extract structured insights from the document.
    Handles legal, academic, or general text with JSON output.
    """

    if not text.strip():
        return {"error": "Empty text"}

    try:
        prompt = f"""
        You are a precise and professional document analyst.
        Read the text below and summarize it into a structured JSON analysis.

        TEXT TO ANALYZE:
        ----------------
        {text}

        Respond strictly in this JSON format:
        {{
            "document_type": "Type of document (e.g. Legal Agreement, Academic Paper, Invoice, etc.)",
            "confidence_level": "Confidence in % (0-100)",
            "language": "Language used",
            "parties": ["List of involved parties, if any"],
            "key_dates": ["Important dates mentioned"],
            "obligations_with_deadlines": ["Main obligations with due dates"],
            "risks": ["List of potential legal or content risks"],
            "recommendations": ["Suggestions for improvement or next steps"],
            "summary": "Brief plain-language summary (4–6 sentences)."
        }}
        """

        model = genai.GenerativeModel(ANALYSIS_MODEL)

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 1000,
                "response_mime_type": "application/json"
            }
        )

        result_text = response.text.strip()

        # Try to parse JSON safely
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError:
            result = {"summary": result_text}

        return result

    except Exception as e:
        return {"error": f"Gemini 2.5 Pro analysis failed: {str(e)}"}


def chunk_text(text: str, chunk_size: int = 4000):
    """
    Simple text chunking (no embeddings).
    Keeps each chunk under token limit for smooth Gemini processing.
    """
    text = text.replace("\n", " ").strip()
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks
