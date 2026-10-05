from langchain_core.prompts import ChatPromptTemplate

from schemas.resourceRecom_schema import ResourceRecommendationResponse


class ResourceRecommendationAgent:
    def __init__(self, llm):
        self.llm = llm

    def recommend(
        self, target_role: str, missing_skills: list[str], resource_context: str
    ):
        resource_recommendation_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    You are an AI learning mentor.

                    Use ONLY resources explicitly provided in Resource Context.
                    Never invent resources, titles, URLs, or providers.

                    Return ONE JSON OBJECT.
                    The root object MUST contain exactly:
                    target_role, skill_plans, usage_guidance.

                    skill_plans MUST be an array of objects.
                    Each object MUST contain:
                    skill, learning_objective, resources.

                    Each resource MUST contain:
                    title, provider, level, resource_type, url, reason.

                    Create plans only for skills that have matching
                    resources in Resource Context.

                    Copy title, provider, level, resource_type, and url
                    from Resource Context.

                    Return JSON only.
                    
                    """,
                ),
                (
                    "human",
                    """
                    Target Role:
                    {target_role}

                    Missing Skills:
                    {missing_skills}

                    Resource Context:
                    {resource_context}

                    Create the learning resource plan in JSON format.
                    """,
                ),
            ]
        )

        self.chain = resource_recommendation_prompt | self.llm.with_structured_output(
            ResourceRecommendationResponse,
            method="json_schema",
            strict=True,
        )

        structured_response = self.chain.invoke(
            {
                "target_role": target_role,
                "missing_skills": ", ".join(missing_skills),
                "resource_context": resource_context,
            }
        )

        return structured_response
