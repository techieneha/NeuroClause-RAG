from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os, requests, hashlib, json, logging
from io import BytesIO
import asyncio
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()
TEAM_TOKEN = os.getenv("TEAM_TOKEN")
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

# ✅ Setup paths and logging
CACHE_DIR = "data/cache"
os.makedirs(CACHE_DIR, exist_ok=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
print("🔐 Expected Header:", f"Bearer {TEAM_TOKEN}")
print("🔑 GEMINI_API_KEY loaded:", bool(GOOGLE_API_KEY))

# ✅ FastAPI app setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Imports from your pipeline
from rag_pipeline.retriever import HybridRetriever
from rag_pipeline.llm_reasoner import reason_over_clauses
from rag_pipeline.agentic_chunker import parse_pdf_to_text, chunk_text

# ✅ Request model
class RunRequest(BaseModel):
    documents: str
    questions: List[str]

# ✅ Main API endpoint
@app.post("/api/v1/hackrx/run")
async def run_hackrx(req: RunRequest, authorization: str = Header(...)):
    expected_auth = f"Bearer {TEAM_TOKEN}"
    if authorization != expected_auth:
        logger.warning("Unauthorized access attempt.")
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        # ✅ Download and hash document
        logger.info("📥 Downloading document...")
        pdf_response = requests.get(req.documents)
        if pdf_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to download document")

        pdf_bytes = pdf_response.content
        pdf_hash = hashlib.md5(pdf_bytes).hexdigest()
        cache_path = os.path.join(CACHE_DIR, f"{pdf_hash}.json")

        # ✅ Load or parse PDF chunks
        if os.path.exists(cache_path):
            logger.info("⚡ Using cached chunks.")
            with open(cache_path, "r") as f:
                chunks = json.load(f)
        else:
            logger.info("🧠 Parsing and chunking PDF.")
            temp_path = f"{pdf_hash}.pdf"
            with open(temp_path, "wb") as f:
                f.write(pdf_bytes)
            text = parse_pdf_to_text(temp_path)
            os.remove(temp_path)
            chunks = chunk_text(text)
            with open(cache_path, "w") as f:
                json.dump(chunks, f)

        if not chunks:
            raise HTTPException(status_code=500, detail="No content extracted from document.")

        # ✅ Perform retrieval and LLM reasoning
        retriever = HybridRetriever()
        retriever.build_faiss_index(chunks)

        async def answer_question(q: str):
            try:
                top_chunks = retriever.search(q, top_k=2)
                result = reason_over_clauses(q, top_chunks)  # Calls Gemini internally
                logger.info(f"✅ Answered using model: {result.get('model_used')} for question: {q}")
                return result.get("final_answer", "Answer not available.")
            except Exception as e:
                logger.error(f"❌ Error while answering question '{q}': {e}")
                return "Answer not available due to an error."

        final_answers = await asyncio.gather(*(answer_question(q) for q in req.questions))
        return {"answers": final_answers}

    except Exception as e:
        logger.exception("💥 Unhandled exception")
        raise HTTPException(status_code=500, detail=str(e))
