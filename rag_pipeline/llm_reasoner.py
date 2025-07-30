import os
import json
import re
import time
import csv
from dotenv import load_dotenv

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

import tiktoken  # for token counting

# Load environment variables
load_dotenv()
ollama_model = os.getenv("MISTRAL_MODEL", "open-mistral-7b")
mistral_key = os.getenv("MISTRAL_API_KEY")

mistral_client = MistralClient(api_key=mistral_key)


def clean_json_from_text(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return {"final_answer": text.strip(), "error": "Invalid JSON returned"}
    return {"final_answer": text.strip()}


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    try:
        enc = tiktoken.encoding_for_model(model)
    except Exception:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def log_token_usage(model: str, prompt: str, response: str):
    prompt_tokens = count_tokens(prompt, model)
    response_tokens = count_tokens(response, model)
    total_tokens = prompt_tokens + response_tokens

    log_path = "token_log.csv"
    file_exists = os.path.isfile(log_path)

    with open(log_path, mode="a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "model", "prompt_tokens", "response_tokens", "total_tokens"])
        writer.writerow([time.time(), model, prompt_tokens, response_tokens, total_tokens])

    print(f"📊 {model} — Prompt: {prompt_tokens}, Response: {response_tokens}, Total: {total_tokens}")


def reason_over_clauses(question: str, chunks: list) -> dict:
    context = "\n\n".join(
        [chunk[0] if isinstance(chunk, tuple) else str(chunk) for chunk in chunks]
    )[:8000]

    prompt = f"""
You are a helpful insurance assistant.

Context:
{context}

Question:
{question}

Respond with valid JSON format:
{{
  "clause_summary": "...",
  "final_answer": "...",
  "justification": "..."
}}
"""
    try:
        messages = [ChatMessage(role="user", content=prompt)]
        response = mistral_client.chat(model=ollama_model, messages=messages)
        output = response.choices[0].message.content
        log_token_usage(ollama_model, prompt, output)
        result = clean_json_from_text(output)
        result["model_used"] = ollama_model
        return result
    except Exception as e:
        return {"error": f"Mistral error: {str(e)}"}
