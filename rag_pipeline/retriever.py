from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os, pickle

class HybridRetriever:
    def __init__(self, embedding_model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None
        self.chunk_texts = []
        self.dimension = 384  # for MiniLM

    def build_faiss_index(self, chunks: list):
        self.chunk_texts = chunks
        embeddings = self.model.encode(chunks, show_progress_bar=True, batch_size=32)
        index = faiss.IndexFlatL2(self.dimension)
        index.add(np.array(embeddings).astype('float32'))
        self.index = index
        return index

    def save(self, path="data/embeddings/faiss.idx"):
        faiss.write_index(self.index, path)
        with open(path + ".meta.pkl", "wb") as f:
            pickle.dump(self.chunk_texts, f)

    def load(self, path="data/embeddings/faiss.idx"):
        self.index = faiss.read_index(path)
        with open(path + ".meta.pkl", "rb") as f:
            self.chunk_texts = pickle.load(f)

    def search(self, query: str, top_k=3):
        query_vec = self.model.encode([query], show_progress_bar=False)
        D, I = self.index.search(np.array(query_vec).astype('float32'), top_k)
        return [(self.chunk_texts[i], float(D[0][idx])) for idx, i in enumerate(I[0])]


if __name__ == "__main__":
    import glob
    os.makedirs("data/embeddings/", exist_ok=True)
    chunk_files = glob.glob("data/processed_chunks/*.txt")
    all_chunks = []

    for file in chunk_files:
        with open(file, "r") as f:
            all_chunks += f.read().split("\n\n---\n\n")

    retriever = HybridRetriever()
    retriever.build_faiss_index(all_chunks)
    retriever.save()
