import spacy

# Load the English NLP model (only once)
nlp = spacy.load("en_core_web_sm")

def parse_query_with_spacy(query: str) -> dict:
    doc = nlp(query)
    
    # Extract named entities
    entities = [ent.text for ent in doc.ents]
    
    # Extract noun chunks
    noun_chunks = [chunk.text for chunk in doc.noun_chunks]

    return {
        "entities": entities,
        "noun_chunks": noun_chunks,
    }
