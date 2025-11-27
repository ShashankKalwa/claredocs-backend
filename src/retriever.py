import os
import json
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
ANALYSIS_MODEL = "gemini-2.5-pro"

def analyze_with_gemini(text: str) -> dict:
    """Analyze document chunk using Gemini 2.5 Pro."""
    if not text.strip():
        return {"error": "Empty text"}

    try:
        prompt = f"""
        You are a precise document analyst.
        Analyze the following text and return structured JSON only.

        TEXT:
        {text}

        JSON FORMAT STRICTLY:
        {{
            "document_type": "",
            "confidence_level": 0,
            "language": "",
            "parties": [],
            "key_dates": [],
            "obligations_with_deadlines": [],
            "risks": [],
            "recommendations": [],
            "summary": ""
        }}
        """

        model = genai.GenerativeModel(ANALYSIS_MODEL)

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 1200,
                "response_mime_type": "application/json"
            }
        )

        # Extract text safely
        result_text = response.text.strip()

        try:
            return json.loads(result_text)
        except:
            return {"summary": result_text}

    except Exception as e:
        return {"error": f"Gemini analysis failed: {e}"}

def chunk_text(text: str, chunk_size: int = 4000):
    """Simple safe text chunking."""
    text = text.replace("\n", " ").strip()
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
