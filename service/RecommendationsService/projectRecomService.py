from agents.projectRec_agent import ProjectRecommendationAgent
from app.config import get_llm
from schemas.projectRecom_schema import ProjectRecommendationResponse
from service.RecommendationsService.consumeCAoutput import CareerAnalysisProvider
from app.core import app_state


class ProjectRecommendationService:
    def __init__(self):
        self.career_analysis_provider = CareerAnalysisProvider()
        self.project_agent = ProjectRecommendationAgent(app_state.llm)

    def project_recommend(self, target_role: str) -> ProjectRecommendationResponse:

        role_analysis = self.career_analysis_provider.get_role_analysis(
            target_role=target_role
        )

        return self.project_agent.project_recommend(
            target_role=role_analysis.role,
            matching_skills=(role_analysis.matching_skills),
            missing_skills=(role_analysis.missing_skills),
            transferable_skills=(role_analysis.transferable_skills),
            evidence=role_analysis.evidence,
        )
