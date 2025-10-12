# backend/main.py

from services.pdf_parser import process_pdf, process_pending_pdfs
from services.embedder import Embedder
from services.vector_store import ChromaVectorStore
from pathlib import Path

def ingest_pdf(pdf_path: str):
    """
    Processes a PDF and stores its chunks + embeddings into Chroma.
    """
    chunks = process_pdf(pdf_path)
    

    embedder = Embedder()
    embeddings = embedder.embed_texts(chunks)

    store = ChromaVectorStore()
    store.add_documents(chunks, embeddings)

    print("\n✅ Ingestion complete. File is now part of your vector database.")


def ingest_pending_pdfs():
    porcessed = process_pending_pdfs()

    print("\n✅ Ingestion complete. File is now part of your vector database.")
    return porcessed

def ask_question(query: str, n_results: int = 3):
    """
    Queries the Chroma vector database for similar content.
    """
    store = ChromaVectorStore()
    results = store.query(query, n_results=n_results)
    return results


if __name__ == "__main__":
    # ---- MENU ----
    print("📘 RAG Knowledge System")
    print("1. Ingest new PDF")
    print("2. Learn from pending PDFs")
    print("3. Ask a question")
    choice = input("Select an option (1/2): ").strip()

    if choice == "1":
        pdf_path = input("\nEnter the path to your PDF: ").strip()
        if not Path(pdf_path).exists():
            print("❌ File not found. Please check the path.")
        else:
            ingest_pdf(pdf_path)

    elif choice == "3":
        query = input("\nEnter your question: ").strip()
        ask_question(query)
    elif choice == "2":
        processed = ingest_pending_pdfs()
        print(f"Processed {processed['number_of_files']} files.")
        print(f"Embedded {processed['embedded_count']} files.")
        print(f"Stored {processed['stored_count']} files in vector database.")
    else:
        print("⚠️ Invalid choice. Exiting.")
