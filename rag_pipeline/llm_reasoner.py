import os
import json
import re
from dotenv import load_dotenv
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError

# ✅ Load environment variables
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
mistral_api_key = os.getenv("MISTRAL_API_KEY")  # ✅ Correct key loading
ollama_model = os.getenv("MISTRAL_MODEL", "mistral")  # Used with Ollama or Mistral endpoint

# ✅ Configure Gemini client
genai.configure(api_key=gemini_api_key)

# ✅ Configure Mistral client
mistral_client = MistralClient(api_key=mistral_api_key)
print("🔑 MISTRAL API key loaded:", bool(mistral_api_key))


def clean_json_from_text(text: str):
    """Extracts and parses JSON from LLM response"""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return {"final_answer": text.strip(), "error": "Invalid JSON returned"}
    return {"final_answer": text.strip()}


def run_with_mistral(question: str, chunks: list) -> dict:
    """Call Mistral LLM with structured JSON prompt"""
    context = "\n\n".join(
        [chunk[0] if isinstance(chunk, tuple) else str(chunk) for chunk in chunks]
    )[:8000]  # ⏱ Prompt length cutoff

    prompt = f"""
You are a helpful insurance assistant.

Context:
{context}

Question:
{question}

Respond in valid JSON format:
{{
  "clause_summary": "...",
  "final_answer": "...",
  "justification": "..."
}}
"""
    try:
        messages = [ChatMessage(role="user", content=prompt)]
        response = mistral_client.chat(model=ollama_model, messages=messages)
        return {
            **clean_json_from_text(response.choices[0].message.content),
            "model_used": ollama_model,
        }
    except Exception as e:
        return {"error": f"Mistral error: {str(e)}"}


def run_with_gemini(question: str, chunks: list, model_name="gemini-1.5-pro") -> dict:
    """Call Gemini LLM and return parsed JSON"""
    try:
        model = genai.GenerativeModel(model_name)
        context = "\n\n".join(
            [chunk[0] if isinstance(chunk, tuple) else str(chunk) for chunk in chunks]
        )[:16000]

        prompt = f"""You are a helpful insurance assistant.

Context:
{context}

Question:
{question}

Return your response in valid JSON format:
{{
  "clause_summary": "...",
  "final_answer": "...",
  "justification": "..."
}}"""

        response = model.generate_content(prompt)
        return {
            **clean_json_from_text(response.text),
            "model_used": model_name,
        }
    except GoogleAPIError as ge:
        return {"error": f"Gemini API error: {str(ge)}"}
    except Exception as e:
        return {"error": f"Gemini error: {str(e)}"}


def reason_over_clauses(question: str, chunks: list) -> dict:
    """Try Gemini first, fallback to Mistral on failure"""
    if gemini_api_key:
        gemini_result = run_with_gemini(question, chunks)
        if not gemini_result.get("error"):
            return gemini_result
        else:
            print("⚠️ Gemini failed, falling back to Mistral:", gemini_result["error"])

    # Fallback to Mistral
    return run_with_mistral(question, chunks)
