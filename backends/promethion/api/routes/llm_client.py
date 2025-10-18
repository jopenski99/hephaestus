from fastapi import APIRouter, Request, Query
from fastapi.responses import StreamingResponse
from promethion.services.rag_query import RAGQueryEngine
router = APIRouter(prefix="/llm", tags=["LLM"])

@router.get("/test-relevance")
def test_relevance():
    question = "Give me all news today"
    
    rag = RAGQueryEngine()
    
    docs = rag.query(question=question, n_results=3)
    return {"question": question, "relevant_docs": docs}
@router.get("/query")
def query_knowledge(
    request: Request,
    question: str = Query(..., description="Your natural language question"),
    n_results: int = Query(3, description="Number of top matching chunks")
):
    """Query the vector database for relevant information."""
    try:
        docs = request.app.state.services.rag_engine.query(question, n_results)
        context = "\n\n".join(docs)
        answer = request.app.state.services.llm.query_llm(context, question)
    except Exception as e:
        return {"error": str(e)}
    return {"question": question,  "answer": answer}

@router.post("/query/stream")
async def stream_query(request: Request):
    body = await request.json()
    question = body.get("question", "")

    docs = request.app.state.services.rag_engine.query(question, 3)
    context = "\n\n".join(docs)

    def generate():
        print(f"🌐 Streaming response for question: {question}")
        for token in request.app.state.services.llm.stream_llm(context, question):
            yield token

    return StreamingResponse(generate(), media_type="text/plain")
