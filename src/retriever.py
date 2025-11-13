import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ANALYSIS_MODEL = "gpt-4o-mini"

def analyze_document_text(text: str) -> dict:
    """
    Ask GPT-4o-mini to extract key details, risks, recommendations, etc.
    Works with any legal, academic, or general PDF content.
    """

    if not text.strip():
        return {"error": "Empty text"}

    try:
        # Prompt crafted to get structured JSON output
        prompt = f"""
        You are a precise and professional legal & document analyst.
        Read the following content and summarize it into a structured analysis.

        TEXT TO ANALYZE:
        ----------------
        {text}

        Respond in JSON format with these fields:
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

        response = client.chat.completions.create(
            model=ANALYSIS_MODEL,
            messages=[
                {"role": "system", "content": "You are a careful, lawful and detail-oriented analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.3
        )

        import json

        result_text = response.choices[0].message.content.strip()

        # Parse model’s JSON safely
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError:
            result = {"summary": result_text}

        return result

    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}


def chunk_text(text: str, chunk_size: int = 4000):
    """
    Splits large text into manageable chunks for analysis.
    Ensures that each chunk roughly fits model token limits.
    """
    text = text.replace("\n", " ").strip()
    chunks = []

    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)

    return chunks
