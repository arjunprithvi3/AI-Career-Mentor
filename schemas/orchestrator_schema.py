from typing import Literal

from pydantic import BaseModel, Field

from schemas.careerAssessment_schema import CareerAssessmentResponse


class OrchestratorRequest(BaseModel):
    message: str


class CareerSummary(BaseModel):
    suitability_summary: str
    matching_skills: list[str]
    missing_skills: list[str]
    transferable_skills: list[str]


class ProjectSummary(BaseModel):
    project_name: str
    difficulty: str
    problem_statement: str
    skills_covered: list[str]
    tech_stack: list[str]


class LearningResourceSummary(BaseModel):
    skill: str
    title: str
    provider: str
    resource_type: str
    level: str

    reason: str


class ActionStep(BaseModel):
    order: int = Field(ge=1)
    title: str
    description: str
    related_skills: list[str]


class OrchestratorResponse(BaseModel):
    status: Literal[
        "completed",
        "clarification_required",
        "partial",
    ]

    response_type: Literal[
        "career_assessment",
        "project_recommendations",
        "resource_recommendations",
        "complete_plan",
        "clarification",
    ]

    target_role: str | None = None
    clarification_question: str | None = None

    career_summary: CareerSummary | None = None
    career_assessment: CareerAssessmentResponse | None = None

    project_recommendations: list[ProjectSummary] = Field(default_factory=list)

    resource_recommendations: list[LearningResourceSummary] = Field(
        default_factory=list
    )

    next_steps: list[ActionStep] = Field(default_factory=list)

    final_guidance: str
