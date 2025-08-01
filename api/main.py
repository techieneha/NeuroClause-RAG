from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List
import os, logging, asyncio
from dotenv import load_dotenv

from rag_pipeline.retriever import load_pdf, embed_chunks, retrieve_with_rerank
from rag_pipeline.llm_reasoner import answer_with_llm
from rag_pipeline.prompt_template import build_prompt


load_dotenv()
TEAM_TOKEN = os.getenv("TEAM_TOKEN", "hackrx_token")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


class RunRequest(BaseModel):
    documents: str  # local file path or URL
    questions: List[str]


@app.post("/api/v1/hackrx/run")
async def run_query(req: RunRequest, authorization: str = Header(...)):
    if authorization != f"Bearer {TEAM_TOKEN}":
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        chunks = load_pdf(req.documents)
        vectorstore = embed_chunks(chunks)

        async def process_question(q):
            top_docs = retrieve_with_rerank(q, vectorstore)
            return await answer_with_llm(q, top_docs)

        answers = await asyncio.gather(*[process_question(q) for q in req.questions])
        return {"answers": answers}

    except Exception as e:
        logger.exception("🔥 Unhandled error:")
        raise HTTPException(status_code=500, detail=str(e))
