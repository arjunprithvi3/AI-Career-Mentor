from agents.resourceRec_agent import ResourceRecommendationAgent
from app.config import get_llm
from app.core import app_state
from rag.jsonIngestion import get_resource_retriever
from service.RecommendationsService.consumeCAoutput import CareerAnalysisProvider


class ResourceRecommendationService:
    def __init__(self):
        self.provider = CareerAnalysisProvider()
        self.retriever = app_state.resource_retriever
        self.agent = ResourceRecommendationAgent(app_state.llm)

    def recommend(self, target_role: str):
        analysis = self.provider.get_role_analysis(target_role)
        missing_skills = analysis.missing_skills
        
        docs = []
        for skill in missing_skills:
            docs.extend(self.retriever.invoke(skill))
        context = "\n\n".join(doc.page_content for doc in docs)
        return self.agent.recommend(
            target_role=target_role,
            missing_skills=missing_skills,
            resource_context=context,
        )
