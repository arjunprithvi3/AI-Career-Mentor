from app.core import app_state
from rag.ingestion import *


class RAGService:
    def ingest_doc(self, file_path: str):
        docs = load_pdf(file_path)
        chunks = split_documents(docs)
        build_vector_store(chunks, app_state.embeddings)
        # refresh global db
        app_state.resume_db = load_vector_store(app_state.embeddings)
        app_state.resume_retriever = get_retriever(app_state.resume_db)
        return {"message": "Document ingested successfully."}

    def search_doc(self, query: str):
        results = app_state.resume_retriever.invoke(query)
        return {"query": query, "results": [doc.page_content for doc in results]}
