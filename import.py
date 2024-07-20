import pandas as pd
import chromadb
import ollama
from tqdm import tqdm

# Load the data from CSV file
df = pd.read_csv('dataset/en.csv', header=None)

# Set column names for better readability
df.columns = ['id', 'url', 'title', 'document']

# Initialize the ChromaDB client and create a collection
client = chromadb.PersistentClient(path="./db/data")
collection_name = "docs"


# If collection exists delete it
try:
  # Check if the collection exists
  if client.get_collection(collection_name) is not None:
    client.delete_collection(collection_name)
    print(f"Collection '{collection_name}' has been deleted.")
except Exception as e:
  print(f"An error occurred: {e}")

# Create a new collection
collection = client.create_collection(collection_name)

# Iterate over the DataFrame with a tqdm progress bar to show progress
for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing documents"):
  # Get the document text and the URL
  document_text = row['document']
  document_url = row['url']

  # Generate the embedding using Ollama
  response = ollama.embeddings(model="mxbai-embed-large", prompt=document_text)
  embedding = response["embedding"]

  # Add the document and its embedding to the collection
  collection.add(
    ids=[document_url],
    embeddings=[embedding],
    documents=[document_text]
  )
