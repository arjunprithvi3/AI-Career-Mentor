from pydantic import BaseModel


class RoleRecommendationRequest(BaseModel):
	
	target_role: str 

