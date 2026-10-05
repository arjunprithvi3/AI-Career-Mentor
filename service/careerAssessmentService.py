from agents.interviewCoach_agent import InterviewCoachAgent
from agents.jobFit_agent import JobFitAgent
from app.core import app_state
from schemas.careerAssessment_schema import (
    CareerAssessmentResponse,
    JobFitAnalysis,
    RankedJobFit,
)


class CareerAssessmentService:
    def __init__(self):

        # resume_embeddings = resume_ingestion.create_embeddings()
        # resume_db = resume_ingestion.load_vector_store(resume_embeddings)

        # job_embeddings = job_ingestion.create_embeddings()
        # job_db = job_ingestion.load_vector_store(job_embeddings)

        self.resume_retriever = app_state.resume_retriever
        self.job_retriever = app_state.job_retriever

        llm = app_state.llm
        self.job_fit_agent = JobFitAgent(llm)
        self.interview_coach_agent = InterviewCoachAgent(llm)

    def assess(self, target_roles: list[str]):

        roles = self._clean_roles(target_roles)
        resume_context = self.retrieve_resume_context()
        role_analyses = []

        for role in roles:
            job_context = self.retrieve_job_context(role)
            analysis = self.job_fit_agent.analyze(
                target_role=role,
                resume_context=resume_context,
                job_context=job_context,
            )
            percentage = self._calculate_fit_percentage(
                matching_skills=analysis.matching_skills,
                missing_skills=analysis.missing_skills,
            )
            role_analyses.append(
                {
                    "role": role,
                    "fit_percentage": percentage,
                    "analysis": analysis,
                }
            )

        sorted_analyses = sorted(
            role_analyses, key=lambda item: item["fit_percentage"], reverse=True
        )

        ranked_roles = []
        for index, item in enumerate(sorted_analyses, start=1):
            ranked_roles.append(
                RankedJobFit(
                    rank=index,
                    role=item["role"],
                    fit_percentage=item["fit_percentage"],
                    analysis=item["analysis"],
                )
            )

        best_match = ranked_roles[0]
        interview_result = self.interview_coach_agent.analyze(
            target_role=best_match.role,
            resume_context=resume_context,
            matching_skills=best_match.analysis.matching_skills,
            missing_skills=best_match.analysis.missing_skills,
            transferable_skills=best_match.analysis.transferable_skills,
        )

        return CareerAssessmentResponse(
            ranked_roles=ranked_roles,
            recommended_role=best_match.role,
            interview_coach=interview_result,
        )

    def retrieve_resume_context(self) -> str:
        resume_query = (
            "technical skills experience projects responsibilities "
            "education certifications"
        )
        documents = self.resume_retriever.invoke(resume_query)
        if not documents:
            raise ValueError(
                "No resume information was found. Upload and ingest a resume first."
            )
        return self.documents_to_context(documents)

    def retrieve_job_context(self, role: str) -> str:
        query = (
            f"{role} required skills preferred skills "
            f"experience responsibilities qualifications"
        )
        documents = self.job_retriever.invoke(query)
        if not documents:
            raise ValueError(f"No job information was found for role: {role}")
        return self.documents_to_context(documents)

    @staticmethod
    def documents_to_context(documents) -> str:
        unique_contents = []
        seen = set()
        for document in documents:
            content = document.page_content.strip()
            if content and content not in seen:
                seen.add(content)
                unique_contents.append(content)
        return "\n\n".join(unique_contents)

    @staticmethod
    def _calculate_fit_percentage(
        matching_skills: list[str], missing_skills: list[str]
    ) -> float:
        matching_count = len(
            {skill.strip().lower() for skill in matching_skills if skill.strip()}
        )
        missing_count = len(
            {skill.strip().lower() for skill in missing_skills if skill.strip()}
        )
        total_required = matching_count + missing_count
        if total_required == 0:
            return 0.0
        percentage = (matching_count / total_required) * 100
        return round(percentage, 2)

    @staticmethod
    def _clean_roles(target_roles: list[str]) -> list[str]:
        cleaned_roles = []
        seen = set()
        for role in target_roles:
            cleaned_role = role.strip()
            if cleaned_role and cleaned_role.lower() not in seen:
                seen.add(cleaned_role.lower())
                cleaned_roles.append(cleaned_role)
        return cleaned_roles

    def analyze_target_role(self, target_role: str) -> JobFitAnalysis:

        cleaned_role = target_role.strip()
        resume_context = self.retrieve_resume_context()
        job_context = self.retrieve_job_context(cleaned_role)

        analysis = self.job_fit_agent.analyze(
            target_role=cleaned_role,
            resume_context=resume_context,
            job_context=job_context,
        )
        return analysis
