from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List
import os
import logging
import asyncio
from dotenv import load_dotenv
from rag_pipeline.retriever import load_pdf, embed_chunks, retrieve_with_rerank  # Fixed import path
from rag_pipeline.llm_reasoner import answer_with_llm

load_dotenv()
TEAM_TOKEN = os.getenv("TEAM_TOKEN", "hackrx_token")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Policy Query Engine (Local)",
    description="RAG system using local Mistral and embeddings"
)

class RunRequest(BaseModel):
    documents: str  # PDF URL
    questions: List[str]

async def process_question(q, vectorstore):
    """Process each question with proper error handling"""
    try:
        top_docs = await retrieve_with_rerank(q, vectorstore)
        return await answer_with_llm(q, top_docs)
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        return "Answer unavailable."

@app.post("/api/v1/hackrx/run")
async def run_query(req: RunRequest, authorization: str = Header(...)):
    if authorization != f"Bearer {TEAM_TOKEN}":
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        # Load and process document
        documents = await load_pdf(req.documents)
        vectorstore = embed_chunks(documents)
        
        # Process all questions in parallel
        answers = await asyncio.gather(*[
            process_question(q, vectorstore)
            for q in req.questions
        ])
        
        return {"answers": answers}

    except Exception as e:
        logger.exception("Processing failed")
        raise HTTPException(500, "Query processing failed")