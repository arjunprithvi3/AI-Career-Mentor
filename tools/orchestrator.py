import json
from typing import Any

from langchain.tools import tool
from pydantic import BaseModel

from app.core import app_state
from service.careerAssessmentService import CareerAssessmentService
from service.RecommendationsService.projectRecomService import (
    ProjectRecommendationService,
)
from service.RecommendationsService.resourceRecomService import (
    ResourceRecommendationService,
)


def serialize_result(result: Any) -> str:

    if isinstance(result, BaseModel):
        return result.model_dump_json(indent=2)
    return json.dumps(result, indent=2, default=str)


def validate_startup() -> None:

    if app_state.llm is None:
        raise RuntimeError("LLM is not initialized.")
    if app_state.resume_retriever is None:
        raise RuntimeError("Resume retriever is not initialized.")
    if app_state.job_retriever is None:
        raise RuntimeError("Job retriever is not initialized.")


@tool
def career_assessment_tool(target_role: str) -> str:
    """
    Analyze the uploaded candidate resume against one
    target career role.
    Use this tool for suitability, matching skills,
    missing skills, transferable skills, strengths,
    evidence, and overall career fit.
    Args:
    target_role:
            Normalized target role such as AI Engineer,
            Java Developer, GenAI Engineer, Machine
            Learning Engineer, or Data Scientist.
    """
    validate_startup()
    service = CareerAssessmentService()
    result = service.analyze_target_role(target_role=target_role.strip())
    return serialize_result(result)


@tool
def project_recommendation_tool(target_role: str) -> str:
    """
    Generate personalized portfolio projects for one
    target career role.
    Use this tool when the user asks what projects to
    build, how to strengthen their portfolio, or how to
    practice missing skills.
    Args:
    target_role:
            Normalized target role such as AI Engineer.
    """
    validate_startup()
    service = ProjectRecommendationService()
    result = service.project_recommend(target_role=target_role.strip())
    return serialize_result(result)


@tool
def resource_recommendation_tool(target_role: str) -> str:
    """
    Recommend curated learning resources for the missing
    skills associated with one target career role.
    Use this tool when the user asks what to learn, where
    to learn it, or requests courses, documentation,
    tutorials, or learning resources.
    Args:
    target_role:
            Normalized target role such as AI Engineer.
    """
    validate_startup()
    if app_state.resource_retriever is None:
        raise RuntimeError("Resource retriever is not initialized.")
    service = ResourceRecommendationService()
    result = service.recommend(target_role=target_role.strip())
    return serialize_result(result)


career_tools = [
    career_assessment_tool,
    project_recommendation_tool,
    resource_recommendation_tool,
]
