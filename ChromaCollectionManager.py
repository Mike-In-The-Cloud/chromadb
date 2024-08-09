import boto3
from botocore.exceptions import ClientError
from typing import List, Dict
from utilities import get_chromadb_client
from CustomEmbedding import get_embedding_function

class ChromaCollectionManager:
    def __init__(self, bucket_name: str, prefix: str, collection_name: str, region_name: str, embedding_model_id: str):
        self.bucket_name = bucket_name
        self.prefix = prefix
        self.collection_name = collection_name
        self.region_name = region_name
        self.embedding_model_id = embedding_model_id
        self.s3_client = boto3.client('s3', region_name='eu-west-1')
        self.client = get_chromadb_client()
        self.embedding_function = get_embedding_function(region_name=self.region_name, model_id=self.embedding_model_id)

    def fetch_data_from_s3(self) -> List[Dict[str, str]]:
        documents = []
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=self.prefix)
            for obj in response.get('Contents', []):
                key = obj['Key']
                response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
                content = response['Body'].read().decode('utf-8')
                documents.append({"content": content, "metadata": {"s3_key": key}})
        except ClientError as e:
            print(f"Error fetching data from S3: {e}")
            return []
        return documents

    def split_text(self, documents: List[Dict[str, str]], max_tokens: int = 1000) -> List[Dict[str, str]]:
        import tiktoken

        encoder = tiktoken.get_encoding("cl100k_base")
        split_docs = []

        for doc in documents:
            tokens = encoder.encode(doc["content"])
            if len(tokens) <= max_tokens:
                split_docs.append(doc)
            else:
                chunks = [tokens[i:i + max_tokens] for i in range(0, len(tokens), max_tokens)]
                for chunk in chunks:
                    split_docs.append({"content": encoder.decode(chunk), "metadata": doc["metadata"]})

        return split_docs

    def create_or_reset_collection(self):
        try:
            self.client.delete_collection(self.collection_name)
            print(f"Deleted existing collection: {self.collection_name}")
        except Exception as e:
            print(f"Collection {self.collection_name} does not exist or could not be deleted: {e}")

        collection = self.client.create_collection(name=self.collection_name, embedding_function=self.embedding_function)
        print(f"Created new collection: {self.collection_name}")
        return collection

    def add_or_update_documents(self, collection, documents: List[Dict[str, str]]):
        texts = [doc["content"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]
        embeddings_list = self.embedding_function(texts)
        print(f"Embeddings created, shape: {len(embeddings_list)}, {len(embeddings_list[0])}")

        ids = [str(i) for i in range(len(documents))]

        collection.add(
            documents=texts,
            embeddings=embeddings_list,
            metadatas=metadatas,
            ids=ids
        )
        print("Documents added/updated in the ChromaDB collection successfully.")

    def run(self):
        # Fetch data from S3
        documents = self.fetch_data_from_s3()

        # Exit if no documents were fetched
        if not documents:
            print("No documents fetched from S3. Exiting.")
            return

        # Split the documents into chunks
        split_documents = self.split_text(documents)

        # Create or reset the collection in ChromaDB
        collection = self.create_or_reset_collection()

        # Add or update documents in the collection
        self.add_or_update_documents(collection, split_documents)

# if __name__ == "__main__":
#     bucket_name = 'dev-chatbot-euwest1-s3'
#     prefix = 'confluence-export/'
#     collection_name = "test_ssm_collection"
#     bedrock_region = "eu-west-2"
#     embedding_model_id = "amazon.titan-embed-text-v2:0"

#     manager = ChromaCollectionManager(
#         bucket_name=bucket_name,
#         prefix=prefix,
#         collection_name=collection_name,
#         region_name=bedrock_region,
#         embedding_model_id=embedding_model_id
#     )

#     manager.run()
