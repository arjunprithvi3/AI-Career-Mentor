from pydantic import BaseModel


class ProjectMilestone(BaseModel):
    order: int
    title: str
    description: str


class ProjectRecommendation(BaseModel):
    project_name: str
    problem_statement: str
    difficulty: str
    skills_covered: list[str]
    tech_stack: list[str]
    milestones: list[ProjectMilestone]


class ProjectRecommendationResponse(BaseModel):
    target_role: str
    recommendations: list[ProjectRecommendation]
