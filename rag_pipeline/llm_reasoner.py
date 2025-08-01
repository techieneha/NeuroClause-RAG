from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from rag_pipeline.prompt_template import build_prompt



async def answer_with_llm(query: str, top_docs):
    context = "\n\n".join(doc.page_content for doc in top_docs)

    prompt = build_prompt(context=context, question=query)
    llm = ChatOllama(model="mistral")
    chain = llm | StrOutputParser()
    response = await chain.ainvoke(prompt)
    return response.strip()
