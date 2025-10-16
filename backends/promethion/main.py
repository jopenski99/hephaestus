# backend/api/main.py

from fastapi import APIRouter, Request, FastAPI, Query, File, UploadFile
from fastapi.responses import StreamingResponse, JSONResponse
from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from promethion.api.core.config import settings
from promethion.api.routes import auth
from promethion.api.routes import knowledge_base
from promethion.api.routes import llm_client
from promethion.services.pdf_parser import PDFParser
from promethion.services.embedder import Embedder
from promethion.services.vector_store import ChromaVectorStore
from promethion.services.rag_query import RAGQueryEngine
from promethion.services.llm_cliet import LLMClient
from promethion.services.db import init_db
from promethion.services.auth import verify_jwt
from promethion.services.rate_limiter import init_rate_limiter, rate_limit
import asyncio



# Always resolve the .env path explicitly
app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, version="0.1.0")

@app.on_event("startup")
async def startup():
    await init_db()
    print("✅ Database initialized")
    await init_rate_limiter()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(llm_client.router)
app.include_router(knowledge_base.router)

# === Service Instances ===
services = {
    "parser" : PDFParser(),
    "embedder" : Embedder(),
    "store" : ChromaVectorStore(),
    "llm" : LLMClient(),
    "rag_engine" : RAGQueryEngine()
}

app.state.services = services
app.state.settings = settings

@app.get("/")
def root():
    return {"message": "Hephaestus RAG API is running 🚀"}

    
# === Scheduled PDF Processor ===
def process_pending_pdfs():
    print("🕒 Scanning for unprocessed PDFs...")
    
    try:
        print(f"📄 Processing pending files")
        data = services["parser"].process_pending_pdfs()

      
        print(f"✅ processed and moved to for_dispose")
        print(data)
    except Exception as e:
            print(f"❌ Error processing {e}")

# === Scheduler ===
scheduler = BackgroundScheduler()
scheduler.add_job(process_pending_pdfs, "interval", minutes=5)
scheduler.start()

print("✅ Background scheduler started. Running every 5 minutes.")