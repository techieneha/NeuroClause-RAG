import logging
import time
from typing import List, Tuple, Union
import httpx

logger = logging.getLogger(__name__)
OLLAMA_LOCAL_URL = "http://localhost:11434/api/generate"

# Accepts top_chunks as List[str] OR List[Tuple[float, str]] OR List[Dict]
def format_prompt(question: str, top_chunks: List[Union[str, Tuple[float, str], dict]]) -> str:
    formatted_chunks = []
    for i, chunk in enumerate(top_chunks):
        if isinstance(chunk, tuple) and isinstance(chunk[1], str):
            formatted_chunks.append(f"[{i+1}] {chunk[1].strip()}")
        elif isinstance(chunk, dict):
            text = chunk.get("text", "").strip()
            formatted_chunks.append(f"[{i+1}] {text}")
        elif isinstance(chunk, str):
            formatted_chunks.append(f"[{i+1}] {chunk.strip()}")
        else:
            logger.warning(f"❌ Unsupported chunk format: {chunk}")
            continue

    context = "\n\n".join(formatted_chunks)

    prompt = f"""
You are a health insurance policy assistant. Based on the below clauses, answer the question accurately, with reference to relevant clause numbers if helpful. Be honest if the answer is not clearly stated.

User Question:
{question}

Relevant Policy Clauses:
{context}

Respond with only the final answer.
""".strip()

    return prompt


async def reason_over_clauses(question: str, top_chunks: List[Union[str, Tuple[float, str], dict]]) -> dict:
    try:
        prompt = format_prompt(question, top_chunks)
        payload = {
            "model": "mistral",
            "prompt": prompt,
            "stream": False,
            "temperature": 0.1,
            "num_predict": 200
        }

        start_time = time.time()
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(OLLAMA_LOCAL_URL, json=payload)
        latency = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            answer = data.get("response", "").strip()
            prompt_tokens = len(prompt.split())
            answer_tokens = len(answer.split())
            total_tokens = prompt_tokens + answer_tokens

            logger.info(f"📊 Mistral local — Prompt Tokens (approx): {prompt_tokens}, Answer Tokens: {answer_tokens}")
            return {
                "final_answer": answer,
                "model_used": "mistral",
                "token_usage": {
                    "prompt_tokens": prompt_tokens,
                    "answer_tokens": answer_tokens,
                    "total_tokens": total_tokens
                },
                "latency": round(latency, 2)
            }
        else:
            logger.error(f"❌ Mistral response error: {response.status_code} {response.text}")
            return {
                "final_answer": "Answer not available.",
                "model_used": "mistral"
            }

    except Exception as e:
        logger.exception(f"💥 Mistral reasoning error: {e}")
        return {
            "final_answer": "Answer not available due to an error.",
            "model_used": "mistral"
        }
