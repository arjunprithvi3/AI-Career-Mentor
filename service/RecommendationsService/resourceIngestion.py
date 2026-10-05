from rag.jsonIngestion import build_vector_store, load_resource_documents


class ResourceIngestionService:
    
    def ingest(self):
        documents = load_resource_documents()
        count = build_vector_store(documents)

        return {"message": "Resources ingested successfully", "documents": count}
