from langchain_core.prompts import ChatPromptTemplate


def build_prompt(context: str, question: str):
    template = (
        "You are a health insurance policy assistant. Your task is to answer user questions "
        "based strictly on the following extracted policy document content.\n\n"
        "If the answer is not present, say 'Not mentioned in the policy document.'\n\n"
        "Question: {question}\n"
        "Context:\n```{context}```"
    )
    return ChatPromptTemplate.from_template(template).format_prompt(context=context, question=question)
