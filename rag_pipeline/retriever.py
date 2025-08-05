from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from sentence_transformers import SentenceTransformer
import tempfile
import httpx
import os
import logging
import numpy as np
from typing import List, Any
import simsimd  # For fast cosine similarity

logger = logging.getLogger(__name__)

# Global model cache
_embedding_model = None

def get_embedding_model() -> SentenceTransformer:
    """Lazy load and cache the embedding model"""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer("BAAI/bge-small-en-v1.5")
    return _embedding_model

async def load_pdf(url: str) -> List[Any]:
    """Optimized PDF loader with memory-efficient streaming"""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)
            response.raise_for_status()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(response.content)
                tmp_path = tmp_file.name

        loader = PyMuPDFLoader(tmp_path)
        try:
            return loader.load()
        finally:
            os.unlink(tmp_path)

    except Exception as e:
        logger.error(f"PDF loading failed: {str(e)}", exc_info=True)
        raise

def embed_chunks(documents: List[Any]) -> FAISS:
    """Optimized embedding pipeline with memory management"""
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        splits = text_splitter.split_documents(documents)

        model = get_embedding_model()
        embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            model_kwargs={"device": "cpu"},
            encode_kwargs={
                "batch_size": 64,
                "convert_to_numpy": True,
                "normalize_embeddings": True
            },
            model=model  # Inject lazy-loaded model
        )

        texts = [doc.page_content for doc in splits]
        metadatas = [doc.metadata for doc in splits]

        return FAISS.from_texts(
            texts=texts,
            embedding=embeddings,
            metadatas=metadatas
        )

    except Exception as e:
        logger.error(f"Embedding failed: {str(e)}", exc_info=True)
        raise

async def retrieve_with_rerank(query: str, vectorstore: FAISS, k: int = 3) -> List[Any]:
    """Hybrid retrieval with optimized performance"""
    try:
        docs = await vectorstore.asimilarity_search(query, k=k*3)

        if len(docs) <= 1:
            return docs[:k]

        query_embedding = np.array(await vectorstore.embeddings.aembed_query(query), dtype=np.float32)

        doc_embeddings = [d.metadata.get("embedding", None) for d in docs]
        doc_embeddings = [e for e in doc_embeddings if e is not None and len(e) > 0]
        doc_embeddings = np.array(doc_embeddings, dtype=np.float32)

        if doc_embeddings.shape[0] == 0:
            return docs[:k]

        scores = simsimd.cosine(query_embedding, doc_embeddings.T)
        sorted_indices = np.argsort(scores)[-k:][::-1]

        return [docs[i] for i in sorted_indices]

    except Exception as e:
        logger.error(f"Retrieval failed: {str(e)}", exc_info=True)
        return await vectorstore.asimilarity_search(query, k=k)
