from utilities import get_chromadb_client
from CustomEmbedding import get_embedding_function
import chromadb

class ChromaQuery:
    def __init__(self, region_name: str, model_id: str):
        # Initialize the embedding function using the helper function
        self.embedding_function = get_embedding_function(region_name, model_id)

        # Get the ChromaDB client from utilities
        self.client = chromadb.HttpClient(host='localhost', port=8000)

    def query_collection(self, collection_name: str, query: str, n_results: int = 5):
        collection = self.client.get_collection(collection_name)
        query_embeddings = self.embedding_function([query])
        results = collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results
        )
        return results
