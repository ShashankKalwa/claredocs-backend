# Legal Document Analyzer Backend

This is the backend service for the Legal Document Analyzer application, which processes and analyzes legal documents using OCR and AI technologies.

## Features

- PDF document processing with text extraction
- OCR capabilities using GPT-4o for image-based documents
- Legal document analysis and information extraction
- RESTful API for document processing and retrieval

## Requirements

- Python 3.11+
- Docker (for containerized deployment)
- Poppler (for PDF processing)

## Setup

### Local Development

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add your OpenAI API key: `OPENAI_API_KEY=your_api_key_here`

3. Run the development server:
   ```
   uvicorn src.main:app --reload
   ```

### Docker Deployment

1. Build the Docker image:
   ```
   docker-compose build
   ```

2. Run the container:
   ```
   docker-compose up
   ```

The API will be available at `http://localhost:8000`.

## API Endpoints

- `POST /upload`: Upload and process a legal document
- `GET /documents/{document_id}`: Retrieve processed document information
- `POST /analyze`: Analyze a previously uploaded document

## Project Structure

- `src/main.py`: Main application entry point and API routes
- `src/ingest.py`: Document processing and text extraction
- `src/generator.py`: Legal document analysis using LLMs
- `src/retriever.py`: Document retrieval functionality
- `src/embeddings.py`: Text embedding generation for document retrieval

## Docker Configuration

The Docker setup includes:
- Python 3.11 slim image
- Poppler for PDF processing
- All required Python dependencies