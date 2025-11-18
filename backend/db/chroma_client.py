import os
import uuid
import chromadb

# Initialize Chroma Cloud client
chroma_client = chromadb.CloudClient(
    api_key=os.getenv("CHROMA_API_KEY"), 
    tenant=os.getenv("CHROMA_TENANT_ID")
)
#collection_name = os.getenv("CHROMA_DB", "Test")
collection_name = "Religion"

collection = chroma_client.get_or_create_collection(collection_name)

def store_vectors(vectors, metadatas, documents):
    """Store vectors, metadata, and chunk text in ChromaDB with unique IDs."""
    # Generate unique IDs for each vector
    ids = [str(uuid.uuid4()) for _ in vectors]
    
    collection.add(
        embeddings=vectors,
        metadatas=metadatas,
        documents=documents,  # Store the chunk text
        ids=ids
    )
    print(f"Inserted {len(vectors)} vectors with unique IDs.")

def retrieve_vectors(query_vector, top_k=5):
    """Retrieve top_k vectors from ChromaDB."""
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k
    )
    return results
