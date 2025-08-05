import logging
import os
import requests
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger(__name__)

# Load config from environment (.env)
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

async def answer_with_llm(query: str, top_docs):
    """
    Generate concise, accurate answers from retrieved clauses using a hosted or local LLM.
    """
    try:
        clauses = [doc.page_content for doc in top_docs]
        prompt = _build_concise_prompt(query, clauses)

        llm = ChatOllama(
            base_url=OLLAMA_URL,
            model=OLLAMA_MODEL,
            temperature=0.1,
            num_ctx=2048
        )

        chain = llm | StrOutputParser()
        response = await chain.ainvoke(prompt)
        return _clean_response(response)

    except Exception as e:
        logger.error(f"LLM reasoning error: {str(e)}")
        return "Answer unavailable."

def _build_concise_prompt(query: str, clauses: list) -> str:
    """
    Builds a structured prompt from query and top clauses.
    """
    return f"""<s>[INST] You are an insurance policy expert. Answer in EXACTLY 1-2 sentences using ONLY these clauses:

{chr(10).join(clauses)}

Question: {query}

Rules:
1. Answer in 1-2 sentences MAX
2. Start with Yes/No if applicable
3. Include ONLY key details
4. Never say "as per clause" or "refer to"
5. Never list multiple conditions
6. Format: [Answer]. [Optional brief condition]

Answer: [/INST]"""

def _clean_response(response: str) -> str:
    """
    Ensure the LLM response is clean and ends with a period.
    """
    response = response.strip()
    if not response.endswith('.'):
        response += '.'
    return response

def call_ollama(prompt: str) -> str:
    """
    Optional direct call to Ollama API (outside LangChain), useful for debugging.
    """
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            }
        )
        return response.json()["response"].strip()
    except Exception as e:
        logger.error(f"Direct Ollama call failed: {str(e)}")
        return "LLM API error."
