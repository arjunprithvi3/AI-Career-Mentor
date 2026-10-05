from pydantic import BaseModel


class GapAnalysis(BaseModel):
    matching_skills: list[str]
    missing_skills: list[str]
    recommendation: str
