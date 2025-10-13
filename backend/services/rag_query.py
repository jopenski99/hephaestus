from backend.services.vector_store import ChromaVectorStore
from sentence_transformers import SentenceTransformer
import numpy as np
from dotenv import load_dotenv

class RAGQueryEngine:
    def __init__(self):
        print("🚀 Initializing RAG Query Engine...")
        self.embedder = SentenceTransformer("all-mpnet-base-v2")
        self.store = ChromaVectorStore()

    def query(self, question: str, n_results: int = 3):
        # Step 1: Embed the query
        print(f"🔍 Embedding query: “{question}”")
        query_embedding = self.embedder.encode([question])

        # Step 2: Query Chroma for similar chunks
        print("📦 Searching vector database...")
        results = self.store.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results
        )

        docs = results["documents"][0]
        scores = results["distances"][0]

        # Step 3: Display results
        #print(f"\n📊 Top {n_results} relevant chunks:\n")
        #for i, (doc, score) in enumerate(zip(docs, scores)):
        #    print(f"{i+1}. Score: {score:.4f}\n{doc[:300]}...\n")

        return docs


if __name__ == "__main__":
    print("RAG Query Engine ready.")
