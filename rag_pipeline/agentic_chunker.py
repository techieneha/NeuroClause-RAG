from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
import os
import re
import fitz  # PyMuPDF


def clean_text(text: str) -> str:
    """Cleans extra whitespace and formatting."""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def chunk_text(text: str, base_chunk_size=1000, overlap=200) -> List[str]:
    """Chunks text using recursive character splitting."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=base_chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    return splitter.split_text(clean_text(text))


def parse_pdf_to_text(file_path: str) -> str:
    """Extracts text from a PDF file using PyMuPDF."""
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def process_and_chunk_all(raw_folder='data/raw', output_folder='data/processed_chunks'):
    """Processes all documents in a folder and chunks them into .txt files."""
    os.makedirs(output_folder, exist_ok=True)
    for filename in os.listdir(raw_folder):
        input_path = os.path.join(raw_folder, filename)

        if filename.endswith('.pdf'):
            print(f"[INFO] Processing PDF: {filename}")
            text = parse_pdf_to_text(input_path)
        elif filename.endswith('.txt'):
            print(f"[INFO] Processing TXT: {filename}")
            with open(input_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            print(f"[SKIP] Unsupported file type: {filename}")
            continue

        chunks = chunk_text(text)
        output_path = os.path.join(output_folder, filename.replace('.pdf', '_chunks.txt').replace('.txt', '_chunks.txt'))
        with open(output_path, 'w', encoding='utf-8') as out:
            out.write("\n\n---\n\n".join(chunks))

        print(f"[DONE] Saved {len(chunks)} chunks to: {output_path}")


if __name__ == "__main__":
    process_and_chunk_all()
