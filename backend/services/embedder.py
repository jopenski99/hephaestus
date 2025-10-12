# backend/services/embedder.py

from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initializes a small, fast embedding model.
        """
        print(f"🔧 Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Takes a list of text chunks and returns a matrix of embeddings.
        """
        print(texts)
        print(f"🧠 Generating embeddings for {len(texts)} chunks...")
        embeddings = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        print(f"✅ Generated embeddings of shape: {embeddings.shape}")
        return embeddings


if __name__ == "__main__":

    print("Embedder ready.")
