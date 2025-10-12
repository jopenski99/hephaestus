# backend/api/main.py

from fastapi import FastAPI, Query, File, UploadFile
from pathlib import Path
import shutil
import json

from apscheduler.schedulers.background import BackgroundScheduler
from backend.services.pdf_parser import PDFParser
from backend.services.embedder import Embedder
from backend.services.vector_store import ChromaVectorStore
from backend.services.rag_query import RAGQueryEngine
from backend.services.llm_cliet import LLMClient

app = FastAPI(title="Hephaestus RAG API")

# Initialize RAG engine once at startup
rag_engine = RAGQueryEngine()

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

@app.get("/query")
def query_knowledge(
    question: str = Query(..., description="Your natural language question"),
    n_results: int = Query(3, description="Number of top matching chunks")
):
    """Query the vector database for relevant information."""
    docs = rag_engine.query(question, n_results)
    context = "\n\n".join(docs)
    answer = llm.query_llm(context, question)
    return {"question": question, "results": docs, "answer": answer}

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