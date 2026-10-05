from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_directory(path: str):
    loader = DirectoryLoader(
        path,
        glob="*.txt",          
        show_progress=True     
    )
    return loader.load()

def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(documents)

def create_embeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"):
    return HuggingFaceEmbeddings(model_name=model_name)

def build_vector_store(documents, embeddings, store_name="job_collection"):
    db = FAISS.from_documents(documents, embeddings)
    db.save_local(f"vector_stores/{store_name}")   
    return db

def load_vector_store(embeddings, store_name="job_collection"):
    return FAISS.load_local(f"vector_stores/{store_name}", embeddings, allow_dangerous_deserialization=True)

def get_retriever(db):
    return db.as_retriever(search_type="similarity", search_kwargs={"k":3})


