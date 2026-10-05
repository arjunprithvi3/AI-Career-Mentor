import rag.ingestion as resume_ingestion
import rag.jobLoader as job_ingestion
from app.config import get_llm
from app.core import app_state
from rag.jsonIngestion import load_vector_store as load_resource_store


def initialize_app():

    print("Loading Embeddings...")
    app_state.embeddings = resume_ingestion.create_embeddings()

    print("Loading LLM...")
    app_state.llm = get_llm()

    print("Loading Resume Store...")
    app_state.resume_db = resume_ingestion.load_vector_store(app_state.embeddings)
    app_state.resume_retriever = resume_ingestion.get_retriever(app_state.resume_db)

    print("Loading Job Store...")
    app_state.job_db = job_ingestion.load_vector_store(
        app_state.embeddings, store_name="job_collection"
    )
    app_state.job_retriever = job_ingestion.get_retriever(app_state.job_db)

    print("Loading Resource Store...")
    app_state.resource_db = load_resource_store()
    app_state.resource_retriever = app_state.resource_db.as_retriever(
        search_kwargs={"k": 5}
    )

    print("Application Initialized")
