from schemas.careerAssessment_schema import JobFitAnalysis
from service.careerAssessmentService import CareerAssessmentService


class CareerAnalysisProvider:
    def __init__(self):
        self.career_assessment_service = CareerAssessmentService()

    def get_role_analysis(self, target_role: str) -> JobFitAnalysis:

        cleaned_role = target_role.strip()
        analysis = self.career_assessment_service.analyze_target_role(
            target_role=cleaned_role
        )

        return analysis
