from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import io
import time
from typing import Dict, Any

from .ingest import DocumentProcessor
from .generator import LegalDocumentAnalyzer
from .retriever import DocumentRetriever
from .utils import validate_file_extension, create_response

app = FastAPI(title="Legal Document Analyzer API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
document_processor = DocumentProcessor()
legal_analyzer = LegalDocumentAnalyzer()
document_retriever = DocumentRetriever()

@app.get("/")
async def root():
    return {"message": "Legal Document Analyzer API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze-document")
async def analyze_document(file: UploadFile = File(...)):
    """
    Analyze a legal document (PDF)
    Uses GPT-4o for OCR if needed, then GPT-4o-mini for analysis
    """
    # Validate file extension
    if not validate_file_extension(file.filename):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Process document (extract text) - this will use GPT-4o for OCR if needed
        start_time = time.time()
        document_text = document_processor.extract_text_from_pdf(file_content)
        
        if not document_text:
            return create_response("error", "Could not extract text from the document")
        
        # Process document for retrieval
        chunks, embeddings = document_retriever.process_document(document_text)
        
        # Extract key information using GPT-4o-mini
        # Pass is_ocr_result flag based on whether OCR was used
        analysis_result = legal_analyzer.extract_key_information(
            document_text, 
            is_ocr_result=document_processor.used_ocr_for_extraction
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Create response
        result = {
            "filename": file.filename,
            "text_length": len(document_text),
            "chunk_count": len(chunks),
            "processing_time": processing_time,
            "ocr_used": document_processor.used_ocr_for_extraction,
            "analysis": analysis_result
        }
        
        return create_response("success", "Document analyzed successfully", result)
    
    except Exception as e:
        return create_response("error", f"Error processing document: {str(e)}")

@app.post("/api/analyze-text")
async def analyze_text(data: Dict[str, Any]):
    """
    Analyze text directly without OCR
    Uses GPT-4o-mini for analysis
    """
    try:
        # Get text from request
        text = data.get("text", "")
        
        if not text:
            return create_response("error", "No text provided")
        
        # Process text
        start_time = time.time()
        
        # Process document for retrieval
        chunks, embeddings = document_retriever.process_document(text)
        
        # Extract key information using GPT-4o-mini
        # Set is_ocr_result to False since this is direct text input
        analysis_result = legal_analyzer.extract_key_information(text, is_ocr_result=False)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Create response
        result = {
            "text_length": len(text),
            "chunk_count": len(chunks),
            "processing_time": processing_time,
            "ocr_used": False,
            "analysis": analysis_result
        }
        
        return create_response("success", "Text analyzed successfully", result)
    
    except Exception as e:
        return create_response("error", f"Error analyzing text: {str(e)}")

@app.post("/api/query-document")
async def query_document(query_data: Dict[str, Any]):
    """
    Query a processed document
    """
    try:
        query = query_data.get("query", "")
        chunks = query_data.get("chunks", [])
        embeddings = query_data.get("embeddings", [])
        
        if not query or not chunks or not embeddings:
            return create_response("error", "Missing required data")
        
        # Retrieve relevant chunks
        results = document_retriever.retrieve_relevant_chunks(query, chunks, embeddings)
        
        return create_response("success", "Query processed successfully", results)
    
    except Exception as e:
        return create_response("error", f"Error processing query: {str(e)}")