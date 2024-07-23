import pandas as pd
import chromadb
import ollama
import argparse

import streamlit as st
from streamlit import components



def min_max_norm(values):
  # Calculate min and max
  min_val = min(values)
  max_val = max(values)

  # Normalize values to start from 1 and end at 0
  return [1 - (x - min_val) / (max_val - min_val) for x in values]

#-------Part 1: RAG Query and Inference prompt -------
def query(prompt, db):
  # Context will hold the text from the relevant documents
  context = ""

  print(f"Prompt:\n{prompt}")
  print(f"RAG On: {db}")

  if db:
    # Initialize the ChromaDB client and create a collection
    client = chromadb.PersistentClient(path="./db/data")
    collection_name = "docs"

    # Connect to the collection
    collection = client.get_collection(collection_name)

    if collection is None:
      print(f"Collection '{collection_name}' does not exist.")
      exit()

    # generate an embedding for the prompt and retrieve the most relevant doc
    queryVector = ollama.embeddings(prompt=prompt, model="mxbai-embed-large")

    # Query the collection using the 'query' method
    results = collection.query(query_embeddings=[queryVector["embedding"]], n_results=10)

    # Simplify access to results
    ids = results['ids'][0]
    docs = results['documents'][0]
    dist = results['distances'][0]

    # If we have relevant documents
    if len(docs) > 0:
      # We'll use norm to normalize the distances
      scores = min_max_norm(dist)
      print(f"{scores}\n\n{ids}\n")

      # Print the query results
      print("\nRelevant documents...")
      for i in range(len(docs)):
        # Only use articles that are within 80% of the most relevant article
        if scores[i] < 0.8:
          break
        print(f"{ids[i]}  Similarity: {scores[i]:.2f}")
        context += " " + docs[i]

  # generate a response combining the prompt and data we retrieved from ChromaDB query
  output = ollama.generate(
    model="llama3.1:8b",
    prompt=f"Review all of this knowledge and combine it with your existing knowledge about the subject of the prompt, use as much of this knowledge as possible in your response: {context}. Respond to this prompt, first give a one sentence summary with 3 bullet points, and then a detailed answer with full context: {prompt}"
  )


  return output['response']

#-------Part 2: CLI Chat -------
# def main():
#     # Create an ArgumentParser object
#     parser = argparse.ArgumentParser(description='Use Wikipedia dataset with open-source LLM and RAG')

#     # Add arguments
#     parser.add_argument('--db', action='store_true', help='Include this switch to use the database')
#     parser.add_argument('--text', default='', type=str, help='Plain text as the second argument')

#     # Parse the arguments and run the LLM generation with/without RAG search
#     args = parser.parse_args()
#     response = query(args.text, args.db)

#     print(f"\n________________________________\n{response}\n________________________________\n\n")


#-------Part 3: Streamlit Web Chat -------
def main():
  # Page configuration
  st.set_page_config(page_title="Wikipedia Enterprise - Sample Dataset RAG")

  # Create containers
  header = st.container()
  user_input = st.container()

  with header:
    st.title("Chat with Wikipedia Dataset")

  user_input = st.text_area("Ask a Question (prompt)", height=150)

  # Checkbox for the user to decide if they want to use the database
  use_db = st.checkbox("Enable RAG assist by demo Wikipedia corpus")

  # Initialize chat history if it's not already in the session state
  if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = ""

  # If the user clicks the "Ask" button and the user input is not empty
  if st.button("Ask the model"):
    if user_input:
      # Get the response from your query function
      response = query(user_input, use_db)

      # Update the chat history with the new interaction
      st.session_state.chat_history = f"{user_input}\n\n{response}\n\n" + "-"*46 + "\n\n" + st.session_state.chat_history

  # Display the updated chat history
  st.text_area("Model Resonse", value=st.session_state.chat_history, height=500, disabled=True)

  if st.button("Clear chat"):
    st.session_state['chat_history'] = ""

if __name__ == "__main__":
    main()
