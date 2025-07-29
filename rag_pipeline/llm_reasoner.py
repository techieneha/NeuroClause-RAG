import ollama
import json
import re

def reason_over_clauses(query: str, top_chunks: list):
    # Format top chunks
    formatted_clauses = "\n".join([f"- {chunk}" for chunk, _ in top_chunks])

    # Build prompt
    prompt = f"""
You are a reasoning assistant for health insurance clauses. Use the clauses provided to answer the user's question as accurately and concisely as possible.

Question: {query}

Clauses:
{formatted_clauses}

Instructions:
- Only use information from the clauses.
- Do not hallucinate.
- Format your answer in valid JSON with these keys:
  - clause_summary: a short summary of relevant clauses
  - final_answer: the concise answer
  - justification: why this answer was chosen

Return JSON:
{{"clause_summary": "...", "final_answer": "...", "justification": "..."}}
"""

    # Call Mistral via Ollama
    response = ollama.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    content = response['message']['content']

    # Optional: extract JSON if wrapped in markdown/code block
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass  # Fallback to raw content if JSON parsing fails

    return {"final_answer": content.strip()}
