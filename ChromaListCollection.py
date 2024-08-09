from chromadb import HttpClient

class ChromaListCollections:
    def __init__(self, host: str = "localhost", port: int = 8000, ssl: bool = False, headers: dict = None):
        # Initialize ChromaDB client
        print(f"Initializing ChromaDB client with host={host}, port={port}, ssl={ssl}")
        self.client = HttpClient(
            host=host,
            port=port,
            ssl=ssl,
            headers=headers or {}
        )
        print(f"ChromaDB client initialized: {self.client}")

    def list_collections(self):
        # List all collections in ChromaDB
        print("Calling list_collections on ChromaDB client.")
        collections = self.client.list_collections()
        if collections is None:
            print("No collections found or client returned None.")
            return []
        print("Collections in ChromaDB:")
        for collection in collections:
            print(f"Collection Name: {collection.name}")
        return collections
