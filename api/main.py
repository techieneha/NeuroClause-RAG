from fastapi import FastAPI, Request, Header, HTTPException
from pydantic import BaseModel
from typing import List
import requests
import os
from rag_pipeline.retriever import HybridRetriever
from rag_pipeline.llm_reasoner import reason_over_clauses

app = FastAPI()

retriever = HybridRetriever()
retriever.load()

TEAM_TOKEN = "26e705335aa7bb76d19ff5dd0d81cba29d83b8b9b81dd4d6eae6c26b7b63d471"

class RunRequest(BaseModel):
    documents: str  # PDF URL
    questions: List[str]

@app.post("/api/v1/hackrx/run")
async def run_submission(req: RunRequest, authorization: str = Header(...)):
    if authorization != f"Bearer {TEAM_TOKEN}":
        raise HTTPException(status_code=401, detail="Invalid token")

    # Step 1: Download and parse document
    file_path = "data/temp.pdf"
    response = requests.get(req.documents)
    with open(file_path, "wb") as f:
        f.write(response.content)

    # Step 2: Parse + chunk (optional: cache if previously parsed)
    from rag_pipeline.agentic_chunker import parse_pdf_to_text, chunk_text

    text = parse_pdf_to_text(file_path)
    chunks = chunk_text(text)

    # Step 3: Build temporary in-memory index
    temp_retriever = HybridRetriever()
    temp_retriever.build_faiss_index(chunks)

    # Step 4: Process each question
    all_answers = []
    for question in req.questions:
        top_chunks = temp_retriever.search(question, top_k=5)
        response = reason_over_clauses(question, top_chunks)
        all_answers.append(response)

    return {"answers": all_answers}
