# backend/api/main.py
from datetime import datetime
from fastapi import FastAPI
import json
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from promethion.api.core.config import settings
from promethion.api.routes import auth
from promethion.api.routes import knowledge_base
from promethion.api.routes import llm_client
from promethion.services.pdf_parser import PDFParser
from promethion.services.embedder import Embedder
from promethion.services.news import News
from promethion.services.vector_store import ChromaVectorStore
from promethion.services.rag_query import RAGQueryEngine
from promethion.services.db import init_db
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
    "rag_engine" : RAGQueryEngine()
}

app.state.services = services
app.state.settings = settings
print("Using "+settings.LLM_NAME+" for LLM")
@app.get("/")
def root():
    return {"message": "Hephaestus RAG API is running 🚀"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/test_llm")
async def test_llm():
    from promethion.services.classifier import GeneralClassifier
    classifier = GeneralClassifier()
    text = "THE DAVAO City Police Office (DCPO) has been recognized as the top-performing unit among all commands under the  Police Regional Office XI for September 2025, according to the official Unit Performance Evaluation Rating (SUPER).\n\nThe consistent achievement is credited to the dynamic leadership of acting city director Colonel Mannan C. Muarip, and the DCPO’s guiding philosophy: the D.A.V.A.O. framework, which stands for Discipline, Action, Virtue, Accountability, and Order.\n\nMuarip lauded the unwavering dedication and personal sacrifices made by the men and women of the DCPO. He noted that their tireless efforts to uphold law, order, and public safety are a powerful testament to their commitment to duty.\n\n“DCPO continues to set the benchmark for outstanding police service,” the statement read, affirming that the D.A.V.A.O. Framework serves as Muarip’s “guiding mantra in leading the organization toward excellence.”\n\nThis accomplishment was not solely due to the police force’s efforts. The DCPO also acknowledged the strong support from the Local Government Unit of Davao City, the active cooperation of barangay officials, and the collective participation of the community.\n\nThe DCPO remains committed to maintaining its status as the “home of disciplined, committed, and service-oriented police officers” as they work together to ensure the continued peace and safety of all Davaoeños."
    response = classifier.classify(text=text)
    return {"response": response}

@app.get("/summarize")
async def summarize_text():
    model_config = {
        "model": settings.LLM_NAME, 
        "port": settings.AI_PORT, 
        "api_key": "", 
        "base_url": settings.AI_HOST}

    news = News(model=model_config)
    text = "Give me all the news for today and Summarize it, Give me your insights on what is happening around me."
    summary = await news.process_news(text=text, type="ioannes_paulus",context_data=None,variant="open-router")
    return {"summary": summary}

@app.get("/collate-and-report")
async def collate_and_report():

    model_config = {
        "model": settings.CLASSIFIER_NAME , 
        "port": settings.CLASSIFIER_PORT, 
        "api_key": settings.CLASSIFIER_KEY, 
        "base_url": settings.CLASSIFIER_URL}

    news = News(model_config)
    context = await news.acquire_news()
    text = "Give me all the news for today and Summarize it, Give me your insights on what is happening around me."
    context_str = ""
    if context:
        if isinstance(context[0], str):
            context_str = "\n\n".join(context)
        else:
            context_str = "\n\n".join([json.dumps(c) for c in context])
    else:
        context_str = ""
    
    summary = await news.process_news(text, "ioannes_paulus", context_str,"open-router")
    return {"summary": summary}

@app.get("/test_rag")
async def test_rag():
    rag  = RAGQueryEngine()
    today = datetime.now().strftime("%Y-%m-%d")
    
    response = rag.query_by_date(date=today,query="Give me all news today")
    return {"response": response}

if __name__ == "__main__":
    asyncio.run(test_llm())
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
""" async def process_pending_pdfs_as_await():
    await services["parser"].process_pending_pdfs(auto_embed=True)

scheduler = BackgroundScheduler()
scheduler.add_job(process_pending_pdfs_as_await, "interval", minutes=5)
scheduler.start() """

print("✅ Background scheduler started. Running every 5 minutes.")