from app.core import app_state
from rag.jobLoader import *


class JobSearchService:

    def ingest_jobs(self, file_path: str):
    
        docs = load_directory(file_path)
        chunks = split_documents(docs)
        embeddings = create_embeddings()
        build_vector_store(chunks, embeddings, store_name="job_collection")
        return {"message": "Document ingested successfully."}

    def rag_query(self, query: str):

        # embeddings = create_embeddings()
        # db = load_vector_store(embeddings, store_name="job_collection")
        # retriever = get_retriever(db)
        results = app_state.job_retriever.invoke(query)
        return {"query": query, "results": [doc.page_content for doc in results]}