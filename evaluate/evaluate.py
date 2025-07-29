import json
from rag_pipeline.retriever import HybridRetriever
from rag_pipeline.llm_reasoner import reason_over_clauses

def evaluate_accuracy(test_file='evaluate/test_set.json'):
    retriever = HybridRetriever()
    retriever.load()
    
    with open(test_file) as f:
        tests = json.load(f)

    correct = 0
    total = len(tests)

    for ex in tests:
        top_chunks = retriever.search(ex['question'])
        answer = reason_over_clauses(ex['question'], top_chunks)
        if ex['expected_answer'].lower() in answer.lower():
            correct += 1

    print(f"Accuracy: {(correct / total) * 100:.2f}%")
