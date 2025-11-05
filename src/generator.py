from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from openai import OpenAI
import os
import json
import logging
from utils import get_env_variable

class LegalDocumentAnalyzer:
    def __init__(self):
        """Initialize the legal document analyzer with OpenAI"""
        api_key = get_env_variable("OPENAI_API_KEY")

        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini" # Using GPT-4o-mini for text analysis

    def extract_key_information(self, text: str, is_ocr_result=False):
        """
        Extract key information from legal document text

        Args:
            text (str): The legal document text
            is_ocr_result (bool): Whether the text came from OCR

        Returns:
            dict: Structured information extracted from the document
        """
        # Limit input length to avoid token overflow
        text = text[:15000]
        
        # Log the source of the text (OCR or direct extraction)
        logging.info(f"Analyzing text (OCR result: {is_ocr_result})")
        
        # Create the prompt with instructions for structured output
        prompt = """
        You are a legal expert analyzing a legal document. Extract the key information from the following text.
        
        TEXT:
        {text}
        
        Extract and return the following information in JSON format:
        - document_type: The specific type of legal document (e.g., "Consulting Agreement", "Income Certificate", "Lease Agreement")
        - confidence_level: A percentage (0-100) indicating your confidence in the analysis
        - language: The language of the document (e.g., "English", "Marathi", "Hindi")
        - parties: List of all parties involved in the document with their roles if identified
        - key_dates: List of all important dates mentioned in the document with context
        - obligations_with_deadlines: List of objects containing {{obligation: "text of obligation", deadline: "deadline date if any", source_offset: "page or paragraph number where found"}}
        - risks: List of objects containing {{risk: "description of risk", recommendation: "recommended non-legal action or advice to consult a lawyer", severity: "high/medium/low"}} (limit to top 3 risks)
        - summary: A comprehensive summary of the document (max 300 words)
        
        IMPORTANT NOTES:
        - If the document is in Marathi or any other Indian language, make sure to identify it correctly and extract all information.
        - For Maharashtra income certificates or any government documents, pay special attention to official seals, signatures, and government department information.
        - Even if you can only extract partial information, provide what you can with appropriate confidence levels.
        - If you cannot determine certain fields, use placeholder values like "Unknown" for text fields or empty arrays for lists, but never leave any field undefined.
        """.format(text=text)
        
        try:
            # Call the OpenAI API with GPT-4o-mini
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a legal document analysis expert. Provide structured JSON output only."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=2000,
                temperature=0.2
            )
            
            # Parse the response
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            # Ensure all required fields are present
            default_fields = {
                "document_type": "Unknown",
                "confidence_level": 0,
                "language": "Unknown",
                "parties": [],
                "key_dates": [],
                "obligations_with_deadlines": [],
                "risks": [],
                "summary": "No summary available"
            }
            
            # Fill in any missing fields with defaults
            for key, default_value in default_fields.items():
                if key not in result or result[key] is None:
                    result[key] = default_value
            
            return result
            
        except Exception as e:
            logging.error(f"Error in document analysis: {str(e)}")
            # Return default structure in case of error
            return {
                "document_type": "Unknown",
                "confidence_level": 0,
                "language": "Unknown",
                "parties": [],
                "key_dates": [],
                "obligations_with_deadlines": [],
                "risks": [],
                "summary": f"Error analyzing document: {str(e)}"
            }
