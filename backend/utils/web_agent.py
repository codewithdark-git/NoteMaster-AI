from langchain.document_loaders import WebBaseLoader
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv('.env')

# check the Groq api set up
if os.getenv('GROQ_API_KEY') is None:
    raise ValueError("GROQ_API_KEY is not set")

def web_agent_flow(link):
    # Load web pages
    loader = WebBaseLoader(link)
    documents = loader.lazy_load()

    # Embed documents and create a vector store
    embeddings = HuggingFaceEmbeddings()
    vector_store = FAISS.from_documents(documents, embeddings)

    # Create a retriever
    retriever = vector_store.as_retriever()

    # Create a QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatGroq(),
        retriever=retriever,
    )

    # Ask a question
    query = "Extract the most important information and overarching theme from the webpage content, ensuring clarity and completeness."
    response = qa_chain.run(query)
    return response.text
