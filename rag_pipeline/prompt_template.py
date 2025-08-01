def build_prompt(query: str, parsed_fields: dict, relevant_clauses: list[str]) -> str:
    prompt = f"""
You are an expert in insurance policy interpretation. Given the user's question and relevant clauses from the policy document, answer concisely, factually, and in a single paragraph.

User Question:
"{query}"

Relevant Policy Clauses:
{chr(10).join([f"- {clause}" for clause in relevant_clauses])}

Instructions:
- Do NOT repeat the clauses.
- DO answer directly with a yes/no if applicable.
- DO justify briefly using facts from the policy.
- DO NOT provide disclaimers.
- DO NOT say "refer to the policy" or "consult the insurer".
- Format the answer in **1-2 precise sentences** using facts only.

Answer:"""
    return prompt.strip()
