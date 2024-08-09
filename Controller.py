#!/usr/bin/python3

import logging
from flask import Flask, jsonify, request
from utilities import check_env_var_exists
from ChromaCollectionManager import ChromaCollectionManager
from ChromaQuery import ChromaQuery
from ChromaListCollection import ChromaListCollections
import os

app = Flask(__name__)

awsProfile=""
region_name = 'eu-west-2'
model_id = 'amazon.titan-embed-text-v2:0'

chromadb_query = ChromaQuery(
    region_name=region_name,
    model_id=model_id
)


@app.route('/')
def health_check():
    return 'Health check of container GET!'

@app.route('/', methods=['POST'])
def testChroma():
    return 'Health check of container POST!'

@app.route('/create-collection', methods=['POST'])
def create_collection():
    # You can extract any necessary parameters from the request if needed
    bucket_name = request.json.get('bucket_name', 'default-bucket')
    prefix = request.json.get('prefix', 'default-prefix/')
    collection_name = request.json.get('collection_name', 'default_collection')
    region_name = request.json.get('region_name', 'eu-west-2')
    embedding_model_id = request.json.get('embedding_model_id', 'amazon.titan-embed-text-v2:0')

    # Instantiate the ChromaCollectionManager class
    manager = ChromaCollectionManager(
        bucket_name=bucket_name,
        prefix=prefix,
        collection_name=collection_name,
        region_name=region_name,
        embedding_model_id=embedding_model_id
    )

    # Run the collection creation process
    try:
        manager.run()
        return jsonify({"message": "Collection created successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/query', methods=['POST'])
def query_chromadb():
    try:
        data = request.json
        collection_name = data.get('collection_name')
        query = data.get('query')
        n_results = data.get('n_results', 5)

        print(f"Querying collection: {collection_name} with query: {query}")

        # Perform the query
        results = chromadb_query.query_collection(collection_name, query, n_results)

        # Extract and return relevant information
        response_data = {
            "ids": results.get('ids', [[]])[0],
            "metadatas": results.get('metadatas', [[]])[0],
            "documents": results.get('documents', [[]])[0],
            "distances": results.get('distances', [[]])[0]
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/list-collections', methods=['GET'])
def list_collections():
    try:
        # Call the list_collections method on the instance
        chroma_manager = ChromaListCollections()
        collections = chroma_manager.list_collections()

        # Convert collections to a list of dictionaries for JSON response
        response_data = [{"name": collection.name} for collection in collections]
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':

    # Get the top-level logger object
    LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
    logging.basicConfig(level = LOGLEVEL)
    logging = logging.getLogger()

    # Register exit handler
    environment_variables = [
    ]

    # Check required environment variables are declared
    for var in environment_variables:
        check_env_var_exists(var)

    app.run(host='0.0.0.0', port=80)
