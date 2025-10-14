from fastapi import APIRouter, Request, Query, UploadFile, File
import shutil
router = APIRouter(prefix="/knowledge_base", tags=["Intellectual Knowledge Base"])

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        return {"error": "Only PDF files are supported."}
    
    save_path = UPLOAD_DIR / file.filename
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
   
    return {
        "filename": file.filename,
        "message": "✅ File processed, embedded, and moved to for_dispose."
    }

@router.post("/immediate_process")
async def immediate_process(request: Request):
        """Endpoint to trigger immediate processing of pending PDFs."""
        try:
            data = request.app.state.services.parser.process_pending_pdfs()
            return {
                "message": "✅ Processed pending PDFs and moved to for_dispose.",
                "data": data
            }
        except Exception as e:
            return {"error": str(e)}
 
@router.post("/clear_vector_store")
def clear_vector_store(request: Request):
    """Endpoint to clear all documents from the vector store."""
    try:
        request.app.state.services.store.clear_collection()
        return {"message": "🗑️ Cleared all documents from vector store."}
    except Exception as e:
        return {"error": str(e)}
