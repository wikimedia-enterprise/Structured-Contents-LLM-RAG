import chromadb

# Initialize the ChromaDB client
client = chromadb.PersistentClient(path="./db/data")
collection_name = "docs"

# Attempt to delete the collection
try:
    # Check if the collection exists
    if client.get_collection(collection_name) is not None:
        client.delete_collection(collection_name)
        print(f"Collection '{collection_name}' has been deleted.")
    else:
        print(f"Collection '{collection_name}' does not exist.")
except Exception as e:
    print(f"An error occurred: {e}")

