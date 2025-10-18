from datetime import datetime
from typing import Dict, List, Optional
from promethion.services.vector_store import ChromaVectorStore
from promethion.services.embedder import Embedder
from promethion.services.classifier import GeneralClassifier

class RAGIngestor:

    def __init__(self):
        self.embedder = Embedder()
        self.vector_store = ChromaVectorStore()
        self.classifier = GeneralClassifier()

    def _prepare_chunks(self, text: str, chunk_size: int = 600, overlap: int = 120) -> List[str]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []
        start = 0
        while start < len(words):
            end = start + chunk_size
            chunks.append(" ".join(words[start:end]))
            start += chunk_size - overlap
        return chunks

    async def ingest_article(self, article: Dict[str, str], category: Optional[str] = None):

        text = f"{article.get('title', '')}\n\n{article.get('content', '')}"
        if not text.strip():
            print("⚠️  Skipping empty article.")
            return

        # Classify if no category provided
        if not category:
            category = self.classifier.classify(text)

        # Chunk text
        chunks = self._prepare_chunks(text)

        # Embed chunks
        embeddings = self.embedder.embed_texts(chunks)

        # Attach metadata
        metadata = {
            "title": article.get("title", "Untitled"),
            "url": article.get("url"),
            "date": article.get("date", str(datetime.utcnow().date())),
            "source": article.get("source", "Unknown"),
            "category": category
        }

        # Store each chunk with metadata
        self.vector_store.collection.add(
            documents=chunks,
            embeddings=embeddings.tolist(),
            metadatas=[metadata] * len(chunks),
            ids=[f"{article.get('url', '')}_{i}" for i in range(len(chunks))]
        )

        print(f"✅ Ingested article: {metadata['title']} ({metadata['category']})")


    async def ingest_batch(self, articles: List[Dict[str, str]]):
        """Batch-ingest a list of articles."""
        for article in articles:
            await self.ingest_article(article)
        print(f"🧩 Ingested {len(articles)} total articles.")