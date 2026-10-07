import os

from dotenv import load_dotenv
from langchain_cohere import CohereEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS

# from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()
cohere_api_key = os.getenv("COHERE_API_KEY")


def load_pdf(file_path: str):
    loader = PyPDFLoader(file_path)
    return loader.load()


def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(documents)


# def create_embeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"):
#     return HuggingFaceEmbeddings(model_name=model_name)


def create_embeddings(model_name="embed-english-v3.0"):
    return CohereEmbeddings(model=model_name, cohere_api_key=cohere_api_key)


def build_vector_store(documents, embeddings, limit=20, store_name="resume_collection"):
    db = FAISS.from_documents(documents[:limit], embeddings)
    db.save_local(f"vector_stores/{store_name}")
    return db


def load_vector_store(embeddings, store_name="resume_collection"):
    return FAISS.load_local(
        f"vector_stores/{store_name}", embeddings, allow_dangerous_deserialization=True
    )


def get_retriever(db):
    return db.as_retriever(search_type="similarity", search_kwargs={"k": 3})


# if __name__ == "__main__":
#     # Step 1: Load PDF
#     docs = load_pdf("C:\\Users\\Arjun Prithvi\\Project\\uploads\\appointment.pdf")

#     # Step 2: Split into chunks
#     chunks = split_documents(docs)

#     # Step 3: Initialize embeddings
#     embeddings = create_embeddings()

#     # Step 4: Build FAISS vector store
#     db = build_vector_store(chunks, embeddings)

#     print("Vector store created with", len(chunks[:20]), "documents.")

#     retriever = get_retriever(db)

#     query = "What is the salary?"
#     results = retriever.invoke(query)

# # Print the retrieved chunks
#     for i, doc in enumerate(results, start=1):
#         print(f"\nResult {i}:")
#         print(doc.page_content)
