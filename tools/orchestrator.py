import json

from langchain.tools import tool

from app.core import app_state
from service.careerAssessmentService import CareerAssessmentService
from service.RecommendationsService.projectRecomService import (
    ProjectRecommendationService,
)
from service.RecommendationsService.resourceRecomService import (
    ResourceRecommendationService,
)


def startup() -> None:
    """
    Confirm that FastAPI startup initialized the
    shared application dependencies.
    """
    if app_state.llm is None:
        raise RuntimeError("LLM is not initialized.")
    if app_state.resume_retriever is None:
        raise RuntimeError("Resume retriever is not initialized.")
    if app_state.job_retriever is None:
        raise RuntimeError("Job retriever is not initialized.")


def error_response(tool_name: str, target_role: str, error: Exception) -> str:
    """
    Return tool failures as data instead of crashing
    the complete agent workflow.
    """
    return json.dumps(
        {
            "tool_name": tool_name,
            "target_role": target_role,
            "success": False,
            "output": None,
            "error": str(error),
        },
        indent=2,
    )


@tool
def career_assessment_tool(target_role: str) -> str:
    """
    Analyze the uploaded candidate resume against one target role.
    Use this tool when the user asks about:
    - suitability for a role
    - matching skills
    - missing skills
    - transferable skills
    - resume evidence
    - career fit
    Args:
    target_role:
            Normalized target role such as AI Engineer,
            GenAI Engineer, Java Developer, Machine
            Learning Engineer, or Data Scientist.
    """
    cleaned_role = target_role.strip()
    try:
        startup()
        service = CareerAssessmentService()
        result = service.analyze_target_role(target_role=cleaned_role)
        return json.dumps(
            {
                "tool_name": ("career_assessment_tool"),
                "target_role": cleaned_role,
                "success": True,
                "output": result.model_dump(),
                "error": None,
            },
            indent=2,
            default=str,
        )
    except Exception as error:  # noqa: BLE001
        return error_response(
            tool_name="career_assessment_tool", target_role=cleaned_role, error=error
        )


@tool
def project_recommendation_tool(target_role: str) -> str:
    """
    Generate personalized portfolio projects for one target role.
    Use this tool when the user asks:
    - what projects they should build
    - how to improve their portfolio
    - how to practice missing skills
    - for project milestones or technology stacks
    Args:
    target_role:
            Normalized target role such as AI Engineer.
    """
    cleaned_role = target_role.strip()
    try:
        startup()
        service = ProjectRecommendationService()
        result = service.project_recommend(target_role=cleaned_role)
        return json.dumps(
            {
                "tool_name": ("project_recommendation_tool"),
                "target_role": cleaned_role,
                "success": True,
                "output": result.model_dump(),
                "error": None,
            },
            indent=2,
            default=str,
        )
    except Exception as error:  # noqa: BLE001
        return error_response(
            tool_name=("project_recommendation_tool"),
            target_role=cleaned_role,
            error=error,
        )


@tool
def resource_recommendation_tool(target_role: str) -> str:
    """
    Retrieve curated learning resources for the candidate's
    missing skills for one target role.
    Use this tool when the user asks:
    - what they should learn
    - where they should learn it
    - for documentation
    - for courses or tutorials
    - for learning resources
    Args:
    target_role:
            Normalized target role such as AI Engineer.
    """
    cleaned_role = target_role.strip()
    try:
        startup()
        if app_state.resource_retriever is None:
            raise RuntimeError("Resource retriever is not initialized.")
        service = ResourceRecommendationService()
        result = service.recommend(target_role=cleaned_role)
        return json.dumps(
            {
                "tool_name": ("resource_recommendation_tool"),
                "target_role": cleaned_role,
                "success": True,
                "output": result.model_dump(),
                "error": None,
            },
            indent=2,
            default=str,
        )
    except Exception as error:  # noqa: BLE001
        return error_response(
            tool_name=("resource_recommendation_tool"),
            target_role=cleaned_role,
            error=error,
        )


career_tools = [
    career_assessment_tool,
    project_recommendation_tool,
    resource_recommendation_tool,
]
