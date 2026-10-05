from agents.resume_agent import ResumeAnalysisAgent
from app.core import app_state
from rag.ingestion import *


class ResumeAnalysisService:

    def analyze_resume(self):

        llm = app_state.llm
        # embeddings = create_embeddings()
        # db = load_vector_store(embeddings)
        retriever = app_state.resume_retriever
        resume_agent = ResumeAnalysisAgent(llm, retriever)
        return resume_agent.analyze_resume()

    

# if __name__ == "__main__":
#     service = ResumeAnalysisService()
#     result = service.analyze_resume()
#     print(result)

