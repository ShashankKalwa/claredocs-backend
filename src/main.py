from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time

# Import your Gemini-based modules
from .generator import perform_gemini_ocr
from .retriever import analyze_with_gemini, chunk_text

app = FastAPI(title="ClareDocs Backend (Gemini 2.5 Pro)")

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict later for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "ClareDocs Gemini Backend is running successfully!"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/api/analyze-document")
async def analyze_document(file: UploadFile = File(...)):
    """Upload a PDF → OCR (Gemini 2.5 Pro) → Chunk → Analyze each part."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        start_time = time.time()
        pdf_bytes = await file.read()

        # Step 1 — OCR using Gemini 2.5 Pro Vision
        ocr_result = perform_gemini_ocr(pdf_bytes)
        full_text = ocr_result.get("text", "")
        total_pages = ocr_result.get("pages", 0)

        if not full_text.strip():
            raise HTTPException(status_code=500, detail="OCR failed: No text extracted.")

        # Step 2 — Chunk the text for analysis
        chunks = chunk_text(full_text, chunk_size=4000)

        # Step 3 — Analyze each chunk using Gemini 2.5 Pro text model
        analyses = []
        for i, chunk in enumerate(chunks, start=1):
            print(f"Analyzing chunk {i}/{len(chunks)}...")
            analysis = analyze_with_gemini(chunk)
            analysis["chunk_number"] = i
            analyses.append(analysis)

        # Step 4 — Merge chunk analyses into one unified report
        summary_texts = [a.get("summary", "") for a in analyses if a]
        combined_summary = "\n\n".join(summary_texts).strip()

        # Calculate average confidence
        try:
            avg_conf = int(
                sum(float(a.get("confidence_level", 0)) for a in analyses) / len(analyses)
            )
        except Exception:
            avg_conf = 0

        elapsed = round(time.time() - start_time, 2)

        return {
            "status": "success",
            "message": "Document analyzed successfully.",
            "report_info": {
                "filename": file.filename,
                "total_pages": total_pages,
                "total_chunks": len(chunks),
                "processing_time": elapsed,
            },
            "analysis": {
                "document_type": analyses[0].get("document_type", "Unknown"),
                "confidence_level": avg_conf,
                "language": analyses[0].get("language", "Unknown"),
                "parties": list({p for a in analyses for p in a.get("parties", [])}),
                "key_dates": list({d for a in analyses for d in a.get("key_dates", [])}),
                "obligations_with_deadlines": list({
                    o for a in analyses for o in a.get("obligations_with_deadlines", [])
                }),
                "risks": list({r for a in analyses for r in a.get("risks", [])}),
                "recommendations": list({rec for a in analyses for rec in a.get("recommendations", [])}),
                "summary": combined_summary or "No summary available.",
            },
            "chunks": [
                {"chunk_number": a["chunk_number"], "summary": a.get("summary", "")}
                for a in analyses
            ],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing document: {str(e)}")
