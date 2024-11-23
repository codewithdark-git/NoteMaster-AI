from langchain.document_loaders import WebBaseLoader
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
import os

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
    query = "Summarize the key points and main topic of the loaded webpage content in a concise manner."
    response = qa_chain.run(query)
    return response

def follow_up_Q(prompt, response):
    follow_up_chain = RetrievalQA.from_chain_type(
        llm=ChatGroq(),
        retriever=retriever,
    )
    follow_up_query = f"Based on the previous response, {prompt}"
    follow_up_response = follow_up_chain.run(follow_up_query)
    return follow_up_response