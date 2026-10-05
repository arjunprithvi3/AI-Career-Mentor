from pydantic import BaseModel
from typing import List
from app.config import get_llm

class ResumeSchema(BaseModel):

    skills: List[str]
    experience: float   
    projects: List[str]
    education: str

