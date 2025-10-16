from fastapi import APIRouter, Request, UploadFile, File,Depends
from sqlmodel import Session
from promethion.services.db import get_session
from promethion.services.auth import verify_token
from promethion.api.core.config import settings
from promethion.services.news import News

import shutil


router = APIRouter(
    prefix="/knowledge_base", 
    tags=["Intellectual Knowledge Base"],
    dependencies=[Depends(verify_token)])

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...),user = Depends(verify_token)):

    if not user or not user.get("su"):
            return {"error": "Unauthorized piece of shit."}

    if not file.filename.lower().endswith(".pdf"):
        return {"error": "Only PDF files are supported."}
    
    save_path = settings.UPLOAD_DIR / file.filename
    print(f"Saving file to: {save_path}")
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
   
    return {
        "filename": file.filename,
        "message": "File uploaded for processing queue."
    }

@router.post("/immediate_process")
async def immediate_process(request: Request, user = Depends(verify_token)):
        """Endpoint to trigger immediate processing of pending PDFs."""
        if not user or not user.get("su"):
            return {"error": "Unauthorized piece of shit."}
        
        try:
            data = request.app.state.services['parser'].process_pending_pdfs()
            return {
                "message": "✅ Processed pending PDFs and moved to for_dispose.",
                "data": data
            }
        except Exception as e:
            return {"error": str(e)}
 
@router.post("/clear_vector_store")
def clear_vector_store(request: Request, user = Depends(verify_token)):

    if not user or not user.get("su"):
        return {"error": "Unauthorized piece of shit."}
    
    try:
        request.app.state.services['store'].clear_collection()
        return {"message": "🗑️ Cleared all documents from vector store."}
    except Exception as e:
        return {"error": str(e)}
    
@router.get("/news-update")
async def news_update(request: Request, user = Depends(verify_token)):

    if not user or not user.get("su"):
        return {"error": "Unauthorized piece of shit."}
    
    #try:
    news = News()
    results =await news.acquire_news()
    return {"message": "✅ News updated.", "results": results}
    #except Exception as e:
    #    return {"error": str(e)}
    

