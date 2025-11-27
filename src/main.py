from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time

from .generator import perform_gemini_ocr
from .retriever import analyze_with_gemini, chunk_text

app = FastAPI(title="ClareDocs Backend (Gemini 3.0 Pro)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def root():
    return {"message": "ClareDocs Gemini Backend is running!"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/analyze-document")
async def analyze_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files supported")

    try:
        start = time.time()
        pdf_bytes = await file.read()

        # 1. OCR
        ocr = perform_gemini_ocr(pdf_bytes)
        text = ocr.get("text", "")
        total_pages = ocr.get("pages", 0)

        if not text.strip():
            raise HTTPException(500, "OCR extraction failed")

        # 2. Chunking
        chunks = chunk_text(text)

        # 3. Per-chunk analysis
        analyses = []
        for i, chunk in enumerate(chunks, 1):
            print(f"Analyzing chunk {i}/{len(chunks)}...")
            analysis = analyze_with_gemini(chunk)
            analysis["chunk_number"] = i
            analyses.append(analysis)

        # Summary merge
        combined_summary = "\n\n".join(
            a.get("summary", "") for a in analyses
        ).strip()

        # Confidence average
        try:
            avg_conf = int(sum(
                int(a.get("confidence_level", 0)) for a in analyses
            ) / len(analyses))
        except:
            avg_conf = 0

        return {
            "status": "success",
            "report_info": {
                "filename": file.filename,
                "total_pages": total_pages,
                "total_chunks": len(chunks),
                "processing_time": round(time.time() - start, 2)
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
                "summary": combined_summary or "No summary available"
            },
            "chunks": [
                {
                    "chunk_number": a["chunk_number"],
                    "summary": a.get("summary", "")
                }
                for a in analyses
            ]
        }

    except Exception as e:
        raise HTTPException(500, f"Error analyzing document: {e}")
