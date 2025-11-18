from db.chroma_client import *

def rag_search(query : str, top_k: int = 5):
    "Search knowledge base for relevant context."
    # Retrieve vectors from ChromaDB
    return retrieve_vectors(query, top_k=top_k)
