from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from rag_pipeline.prompt_template import build_prompt



"""async def answer_with_llm(query: str, top_docs):
    context = "\n\n".join(doc.page_content for doc in top_docs)

    prompt = build_prompt(context=context, question=query)
    llm = ChatOllama(model="mistral")
    chain = llm | StrOutputParser()
    response = await chain.ainvoke(prompt)
    return response.strip()"""


async def answer_with_llm(query: str, top_docs):
    # Build list of clause strings
    relevant_clauses = [doc.page_content for doc in top_docs]

    # Build prompt using correct args
    prompt = build_prompt(
        query=query,
        parsed_fields={},  # Pass an empty dict unless you have structured fields
        relevant_clauses=relevant_clauses
    )

    # Load model and chain
    llm = ChatOllama(model="mistral")
    chain = llm | StrOutputParser()

    # Run async inference
    response = await chain.ainvoke(prompt)
    return response.strip()
