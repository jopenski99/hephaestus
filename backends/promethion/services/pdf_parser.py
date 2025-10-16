import os
import re
import shutil
import pdfplumber

from pathlib import Path
from typing import List

from promethion.services.embedder import Embedder
from promethion.services.vector_store import ChromaVectorStore


class PDFParser:
    def __init__(self):
        self.vector_store = ChromaVectorStore()
        self.embedder = Embedder()

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract all selectable text from a PDF."""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"File not found: {pdf_path}")

        full_text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"

        return full_text.strip()

    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        text = re.sub(r'\s+', ' ', text)  # replace multiple spaces/newlines with single space
        text = re.sub(r'0{3,}', '', text)
        text = re.sub(r'(?<=\w)\.(?=\w)', '', text)  # replace multiple newlines with single newline
        text = re.sub(r'[○]', '', text)
        text += text +"\n"
        return text.strip()

    def chunk_text(self, text: str, chunk_size: int = 600, overlap: int = 120) -> List[str]:
        """Split text into overlapping word chunks."""
        words = text.split()
        chunks = []
        start = 0
        while start < len(words):
            end = start + chunk_size
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            start += chunk_size - overlap  # overlap between chunks
        return chunks

    def process_pdf(self, pdf_path: str, chunk_size: int = 600) -> List[str]:
        """Extract, clean, and chunk a single PDF."""
        print(f"📄 Processing PDF: {pdf_path}")
        text = self.extract_text_from_pdf(pdf_path)
        cleaned = self.clean_text(text)
        chunks = self.chunk_text(cleaned, chunk_size=chunk_size)
        print(f"✅ Extracted {len(chunks)} chunks from {Path(pdf_path).name}")

        # Move processed file to dump dir
        dump_dir = Path(__file__).resolve().parent.parent / "data" / "dump"
        dump_dir.mkdir(parents=True, exist_ok=True)

        destination = dump_dir / Path(pdf_path).name
        shutil.move(pdf_path, destination)
        print(f"🗂️ Moved processed file to: {destination}")

        return chunks

    def process_pending_pdfs(self, auto_embed: bool = True) -> None:
        """Check knowledge_files folder and process any new PDFs."""
        base_dir = Path(__file__).resolve().parent.parent
        knowledge_files_path = base_dir / "data" / "knowledge_files"
        knowledge_files_path.mkdir(parents=True, exist_ok=True)

        pdf_files = [f for f in knowledge_files_path.glob("*.pdf")]
        number_of_files = len(pdf_files)
        embedded_count = 0
        stored_count = 0

        if not pdf_files:
            print("📂 No new PDFs to process.")
            return

        print(f"📚 Found {number_of_files} PDFs to process.")
        for file in pdf_files:
            try:
                chunks = self.process_pdf(str(file))
                if auto_embed:
                    embeddings = self.embedder.embed_texts(chunks)
                    embedded_count += 1
                    self.vector_store.add_documents(chunks, embeddings)
                    stored_count += 1
            except Exception as e:
                print(f"❌ Error processing {file.name}: {e}")

        print(f"✅ Process complete. Embedded: {embedded_count}, Stored: {stored_count}")


if __name__ == "__main__":
    parser = PDFParser()
    parser.process_pending_pdfs()
