# backend/services/vector_store.py

import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path
import uuid


class ChromaVectorStore:
    def __init__(self):
        # Define absolute persistent path
        db_path = Path(__file__).resolve().parent.parent / "data/vector_db"
        #print(f"📦 Using Chroma DB at: {db_path}")
        db_path.mkdir(parents=True, exist_ok=True)

        # ✅ Use PersistentClient (NOT Client)
        self.client = chromadb.PersistentClient(path=str(db_path))
        #print(f"📦 Chroma Persistent DB initialized at: {db_path}")

        # Use consistent collection name
        self.collection = self.client.get_or_create_collection(name="akashic_records")
        print(f"📦 Using collection: {self.collection.name}")
    def clear_collection(self):
        """Deletes all documents in the collection."""
        self.client.delete_collection(name="akashic_records")
        self.collection = self.client.get_or_create_collection(name="akashic_records")
        print("🗑️ Cleared all documents from vector store.")
    
    def add_documents(self, texts, embeddings):
        """Adds text chunks and their embeddings into Chroma."""
        ids = [str(uuid.uuid4()) for _ in texts]
        self.collection.add(
            documents=texts,
            embeddings=embeddings.tolist(),
            ids=ids
        )
        print(f"✅ Added {len(texts)} documents to vector store")
        print(f"📊 Total after insert: {self.collection.count()}")

    def query(self, query_text, n_results=3):
        """Performs a similarity search."""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        docs = results["documents"][0]
        print(f"\n🔍 Top {n_results} results for: “{query_text}”\n")
        for i, d in enumerate(docs):
            print(f"Result {i+1}: {d[:150]}...\n")
        return docs

    def show_all_documents(self, limit: int = 5):
        """List stored documents."""
        results = self.collection.get(limit=limit)
        count = len(results["ids"])
        print(f"📊 Total documents in collection: {count}")
        if count > 0:
            for i, doc in enumerate(results["documents"]):
                print(f"\nDocument {i+1}:\n{doc[:200]}...\n")
        else:
            print("⚠️ No documents found in the vector database.")


if __name__ == "__main__":
    print("Chroma Vector Store ready.")
