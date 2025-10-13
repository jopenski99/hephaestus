# backend/api/main.py

from fastapi import APIRouter, Request, FastAPI, Query, File, UploadFile
from fastapi.responses import StreamingResponse, JSONResponse
import json
from pathlib import Path
import shutil


from apscheduler.schedulers.background import BackgroundScheduler
from backend.services.pdf_parser import PDFParser
from backend.services.embedder import Embedder
from backend.services.vector_store import ChromaVectorStore
from backend.services.rag_query import RAGQueryEngine
from backend.services.llm_cliet import LLMClient

app = FastAPI(title="Hephaestus RAG API")

# Initialize RAG engine once at startup
rag_engine = RAGQueryEngine()

router = APIRouter()

# === Directories ===
UPLOAD_DIR = Path("backend/data/knowledge_files")
DISPOSE_DIR = Path("backend/data/for_dispose")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DISPOSE_DIR.mkdir(parents=True, exist_ok=True)

# === Service Instances ===
parser = PDFParser()
embedder = Embedder()
store = ChromaVectorStore()
llm = LLMClient()

@app.get("/")
def root():
    return {"message": "Hephaestus RAG API is running 🚀"}
@app.get("/test-relevance")
def test_relevance():
    question = "Where is the toolkit located?"
    docs = rag_engine.query(question, n_results=3)
    return {"question": question, "relevant_docs": docs}
@app.get("/query")
def query_knowledge(
    question: str = Query(..., description="Your natural language question"),
    n_results: int = Query(3, description="Number of top matching chunks")
):
    """Query the vector database for relevant information."""
    try:
        docs = rag_engine.query(question, n_results)
        context = "\n\n".join(docs)
        answer = llm.query_llm(context, question)
    except Exception as e:
        return {"error": str(e)}
    return {"question": question,  "answer": answer}

@app.post("/query/stream")
async def stream_query(request: Request):
    body = await request.json()
    print(body)
    question = body.get("question", "")

    docs = rag_engine.query(question, 3)
    context = "\n\n".join(docs)

    def generate():
        for token in llm.stream_llm(context, question):
            yield token

    return StreamingResponse(generate(), media_type="text/plain")

@app.post("/upload")
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

@app.post("/immediate_process")
async def immediate_process():
        """Endpoint to trigger immediate processing of pending PDFs."""
        try:
            data = parser.process_pending_pdfs()
            return {
                "message": "✅ Processed pending PDFs and moved to for_dispose.",
                "data": data
            }
        except Exception as e:
            return {"error": str(e)}
 
@app.post("/clear_vector_store")
def clear_vector_store():
    """Endpoint to clear all documents from the vector store."""
    try:
        store.clear_collection()
        return {"message": "🗑️ Cleared all documents from vector store."}
    except Exception as e:
        return {"error": str(e)}
    
# === Scheduled PDF Processor ===
def process_pending_pdfs():
    print("🕒 Scanning for unprocessed PDFs...")
    
    try:
        print(f"📄 Processing pending files")
        data = parser.process_pending_pdfs()

      
        print(f"✅ processed and moved to for_dispose")
        print(data)
    except Exception as e:
            print(f"❌ Error processing {e}")

# === Scheduler ===
scheduler = BackgroundScheduler()
scheduler.add_job(process_pending_pdfs, "interval", minutes=5)
scheduler.start()

print("✅ Background scheduler started. Running every 5 minutes.")