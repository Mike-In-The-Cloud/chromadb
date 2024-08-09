from langchain_aws import BedrockEmbeddings
from typing import List

# Wrapper function to conform to ChromaDB's expected embedding function interface
class EmbeddingFunctionWrapper:
    def __init__(self, bedrock_embeddings):
        self.bedrock_embeddings = bedrock_embeddings

    def __call__(self, input: List[str]) -> List[List[float]]:
        return self.bedrock_embeddings.embed_documents(input)

# Function to initialize and return the embedding function
def get_embedding_function(region_name: str, model_id: str):
    # Initialize the Bedrock Embeddings
    bedrock_embeddings = BedrockEmbeddings(
        model_id=model_id,
        region_name=region_name
    )

    # Create and return the wrapper instance
    return EmbeddingFunctionWrapper(bedrock_embeddings)