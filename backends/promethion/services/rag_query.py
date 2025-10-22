from datetime import datetime
from chromadb import Client
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


from promethion.services.vector_store import ChromaVectorStore
from promethion.api.core.config import settings

class RAGQueryEngine:
    def __init__(self):
        model_name = settings.EMBEDDER_NAME
        self.embedder = SentenceTransformer(model_name)
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

        return results

    def query_by_date(self,date: str | None = None, query: str = "", n_results: int = 10):
        # Default to today
        if not date:
            date = datetime.now().date().isoformat()

        print(f"📰 Fetching news for date: {date}")
        query_embedding = None

        if query:
            query_embedding = self.embedder.encode([query])
            print(f"🔍 Ranking by query relevance: “{query}”")

        query_args = {
            "n_results": n_results,
            "where": {"date": date}
        }
        print("=" * 60 )
        print(query_args)
        if query_embedding is not None:
            query_args["query_embeddings"] = query_embedding.tolist()

        results = self.store.collection.query(**query_args)

        docs = results["documents"][0]
        metadatas = results["metadatas"][0]
        scores = results.get("distances", [[None]])[0]  # distances if query was used

        # Combine docs with relevance (if applicable)
        combined = []
        for i, doc in enumerate(docs):
            entry = {"document": doc, "metadata": metadatas[i]}
            if query_embedding is not None and scores[i] is not None:
                entry["relevance"] = float(scores[i])
            combined.append(entry)

        # Sort by relevance if available, otherwise by timestamp
        if query_embedding is not None:
            combined.sort(key=lambda x: x["relevance"])
        else:
            combined.sort(key=lambda x: x["metadata"].get("timestamp", ""), reverse=True)

        print(f"✅ Retrieved {len(combined)} news items.")
        return combined
    
    def normalize_chroma_timestamps(collection_name: str, persist_dir: str):
        """
        Cleans all metadata timestamps in a Chroma collection by converting
        full ISO timestamps to date-only format (YYYY-MM-DD).
    
        Args:
            collection_name (str): The name of the Chroma collection to update.
            persist_dir (str): Path to the directory where Chroma persists data.
        """
    
        print(f"🧠 Connecting to Chroma at: {persist_dir}")
        client = Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_dir
        ))
    
        collection = client.get_collection(collection_name)
        print(f"📚 Loaded collection: {collection_name}")
    
        # Fetch all items (include embeddings so we can reinsert them)
        print("📦 Fetching all data...")
        all_data = collection.get(include=["documents", "metadatas", "embeddings"])
    
        total = len(all_data["ids"])
        print(f"🔍 Found {total} records.")
    
        updated_metadatas = []
        fixed = 0
    
        for meta in all_data["metadatas"]:
            if "timestamp" in meta:
                try:
                    # Convert ISO datetime to date-only
                    dt = datetime.fromisoformat(meta["timestamp"])
                    meta["timestamp"] = dt.date().isoformat()
                    fixed += 1
                except Exception:
                    # already date-only or invalid format, skip
                    pass
            updated_metadatas.append(meta)
    
        # Delete all and reinsert (Chroma doesn’t support in-place metadata updates)
        print(f"♻️ Updating {fixed} records with date-only timestamps...")
        collection.delete(ids=all_data["ids"])
        collection.add(
            ids=all_data["ids"],
            documents=all_data["documents"],
            metadatas=updated_metadatas,
            embeddings=all_data["embeddings"]
        )
    
        print(f"✅ Update complete: {fixed}/{total} items normalized.")
if __name__ == "__main__":
    # Example usage
    rge = RAGQueryEngine()
    rge.normalize_chroma_timestamps(
        collection_name="news_articles",     # your Chroma collection name
        persist_dir="C:/Dev/hephaestus/chroma_db"  # adjust to your setup
    )
