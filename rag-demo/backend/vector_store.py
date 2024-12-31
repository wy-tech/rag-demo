import json
import os

from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings

def setup_vector_store(file_path="data/text_list.json"):
    # Create document list
    with open(file_path, "r") as json_file:
        loaded_list = json.load(json_file)
    documents = []
    for content,metadata in loaded_list:
        documents.append(Document(page_content=content, metadata=metadata))

        
    # Directory for persistent storage
    vectorstore_dir = "chroma_db"

    # Create the directory if it doesn't exist
    if not os.path.exists(vectorstore_dir):
        os.makedirs(vectorstore_dir)

    # Initialize embeddings
    embedding = OpenAIEmbeddings()

    # Load or create the Chroma vector store with persistent storage
    vector_store = Chroma.from_documents(documents, embedding, persist_directory=vectorstore_dir)
    return vector_store