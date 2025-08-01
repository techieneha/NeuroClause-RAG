from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder

from typing import List


def load_pdf(path: str):
    loader = PyPDFLoader(path)
    pages = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.split_documents(pages)


def embed_chunks(chunks):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.from_documents(chunks, embeddings)


def load_reranker():
    return CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def retrieve_with_rerank(query: str, vectorstore, top_k: int = 5):
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})
    retrieved = retriever.get_relevant_documents(query)

    reranker = load_reranker()
    pairs = [[query, doc.page_content] for doc in retrieved]
    scores = reranker.predict(pairs)

    reranked = sorted(zip(retrieved, scores), key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in reranked[:top_k]]
