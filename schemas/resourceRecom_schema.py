from pydantic import BaseModel


class LearningResource(BaseModel):
    title: str
    provider: str
    level: str
    resource_type: str
    url: str
    reason: str


class SkillResourcePlan(BaseModel):
    skill: str
    learning_objective: str
    resources: list[LearningResource]


class ResourceRecommendationResponse(BaseModel):
    target_role: str
    skill_plans: list[SkillResourcePlan]
    usage_guidance: str
