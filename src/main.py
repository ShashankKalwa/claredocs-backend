from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
from .generator import perform_gpt4o_ocr
from .retriever import analyze_document_text, chunk_text

app = FastAPI(title="ClareDocs Backend")

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "ClareDocs Backend is running successfully!"}


@app.post("/api/analyze-document")
async def analyze_document(file: UploadFile = File(...)):
    """Upload a PDF → OCR → Chunk → Analyze each part."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        start_time = time.time()
        pdf_bytes = await file.read()

        # Step 1 — OCR
        ocr_result = perform_gpt4o_ocr(pdf_bytes)
        full_text = ocr_result["text"]
        total_pages = ocr_result["pages"]

        if not full_text.strip():
            raise HTTPException(status_code=500, detail="OCR failed: No text extracted.")

        # Step 2 — Chunking
        chunks = chunk_text(full_text, chunk_size=4000)

        # Step 3 — Analyze each chunk
        analyses = []
        for i, chunk in enumerate(chunks, start=1):
            print(f"Analyzing chunk {i}/{len(chunks)}...")
            analysis = analyze_document_text(chunk)
            analysis["chunk_number"] = i
            analyses.append(analysis)

        # Step 4 — Merge results
        summary_texts = [a.get("summary", "") for a in analyses if a]
        combined_summary = "\n\n".join(summary_texts)

        elapsed = round(time.time() - start_time, 2)
        return {
            "status": "success",
            "message": "Document analyzed successfully.",
            "report_info": {
                "filename": file.filename,
                "total_pages": total_pages,
                "total_chunks": len(chunks),
                "processing_time": elapsed
            },
            "analysis": {
                "document_type": analyses[0].get("document_type", "Unknown"),
                "confidence_level": sum(a.get("confidence_level", 0) for a in analyses) // len(analyses),
                "language": analyses[0].get("language", "Unknown"),
                "parties": list({p for a in analyses for p in a.get("parties", [])}),
                "key_dates": list({d for a in analyses for d in a.get("key_dates", [])}),
                "obligations_with_deadlines": list({o for a in analyses for o in a.get("obligations_with_deadlines", [])}),
                "risks": list({r for a in analyses for r in a.get("risks", [])}),
                "recommendations": list({rec for a in analyses for rec in a.get("recommendations", [])}),
                "summary": combined_summary or "No summary available."
            },
            "chunks": [
                {
                    "chunk_number": a["chunk_number"],
                    "summary": a["summary"],
                } for a in analyses
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing document: {str(e)}")

