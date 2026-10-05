from pydantic import BaseModel, Field


class JobFitAnalysis(BaseModel):
    role: str
    matching_skills: list[str] = []
    missing_skills: list[str] = []
    transferable_skills: list[str] = []
    evidence: list[str] = Field(default_factory=list)
    suitability_summary: str


class RankedJobFit(BaseModel):
    rank: int
    role: str
    fit_percentage: float
    analysis: JobFitAnalysis


class InterviewQuestion(BaseModel):
    question: str
    category: str
    difficulty: str
    evaluates: str
    preparation_hint: str


class InterviewCoachResult(BaseModel):
    target_role: str
    focus_areas: list[str] = []
    questions: list[InterviewQuestion] = []


class CareerAssessmentResponse(BaseModel):
    ranked_roles: list[RankedJobFit]
    recommended_role: str
    interview_coach: InterviewCoachResult
