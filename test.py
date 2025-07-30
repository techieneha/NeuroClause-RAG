import os
import json
import hashlib
import time
import requests
from dotenv import load_dotenv

from rag_pipeline.retriever import HybridRetriever
from rag_pipeline.llm_reasoner import reason_over_clauses
from rag_pipeline.agentic_chunker import parse_pdf_to_text, chunk_text

# ✅ Load environment variables
load_dotenv()

# ✅ Input
PDF_URL = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"
QUESTIONS = [
    "What is the grace period for renewal?",
    "What is the waiting period for pre-existing diseases?",
    "Does the policy cover maternity expenses? If yes, what are the conditions?",
    "What is the waiting period for cataract surgery?",
    "Does the policy cover organ donor expenses?",
    "Is there a no claim discount?",
    "Are health check-up expenses reimbursed?",
    "How is a hospital defined in the policy?",
    "Does the policy cover AYUSH treatment?",
    "What is the room rent limit for Plan A?"
]

CACHE_DIR = "data/cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# ✅ Measure latency
start_time = time.time()

# ✅ Download PDF
print("📥 Downloading PDF...")
response = requests.get(PDF_URL)
if response.status_code != 200:
    raise Exception("Failed to download PDF")

pdf_bytes = response.content
pdf_hash = hashlib.md5(pdf_bytes).hexdigest()
cache_path = os.path.join(CACHE_DIR, f"{pdf_hash}.json")

# ✅ Use cache if available
if os.path.exists(cache_path):
    print("⚡ Using cached chunks.")
    with open(cache_path, "r") as f:
        chunks = json.load(f)
else:
    print("🧠 Parsing and chunking PDF...")
    with open(f"{pdf_hash}.pdf", "wb") as f:
        f.write(pdf_bytes)
    text = parse_pdf_to_text(f"{pdf_hash}.pdf")
    os.remove(f"{pdf_hash}.pdf")
    chunks = chunk_text(text)
    with open(cache_path, "w") as f:
        json.dump(chunks, f)

# ✅ Retrieval + LLM reasoning
print("🔍 Retrieving + reasoning...")
retriever = HybridRetriever()
retriever.build_faiss_index(chunks)

final_answers = []

for question in QUESTIONS:
    top_chunks = retriever.search(question, top_k=2)
    result = reason_over_clauses(question, top_chunks)
    if "final_answer" in result:
        final_answers.append(result["final_answer"])
    else:
        final_answers.append(result.get("error", "Could not generate answer"))

# ✅ Print response
end_time = time.time()
print(json.dumps({"answers": final_answers}, indent=4))
print(f"\n⏱️ Total Latency: {end_time - start_time:.2f} seconds")
