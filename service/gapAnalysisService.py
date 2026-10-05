from agents.gapAnalysis_agent import GapAnalysisAgent
from app.core import app_state


class GapAnalysisService:
    
    def analyze(self, target_role: str):
      
        # resume_embeddings = resume_ingestion.create_embeddings()
        # resume_db = resume_ingestion.load_vector_store(resume_embeddings)

      
        # job_embeddings = job_ingestion.create_embeddings()
        # job_db = job_ingestion.load_vector_store(job_embeddings)
        
       
        # resume_retriever = resume_ingestion.get_retriever(resume_db)
        # job_retriever = job_ingestion.get_retriever(job_db)
        
        resume_docs = app_state.resume_retriever.invoke("skills projects experience")
        job_docs = app_state.job_retriever.invoke(target_role)
       
        resume_context = "\n".join(doc.page_content for doc in resume_docs)
        job_context = "\n".join(doc.page_content for doc in job_docs)

        llm = app_state.llm
        agent = GapAnalysisAgent(llm)

        return agent.analyze_gap(resume_context, job_context)
