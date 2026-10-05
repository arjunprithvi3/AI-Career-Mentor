from langchain_core.prompts import ChatPromptTemplate

from schemas.projectRecom_schema import ProjectRecommendationResponse


class ProjectRecommendationAgent:
    def __init__(self, llm):
        self.llm = llm

    def project_recommend(
        self,
        target_role: str,
        matching_skills: list[str],
        missing_skills: list[str],
        transferable_skills: list[str],
        evidence: list[str],
    ):

        project_recommendation_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    You are an AI engineering project mentor.

                    Recommend exactly 3 practical, real-world portfolio projects based ONLY
                    on the candidate information provided.

                    Projects must be:
                    1. Foundational
                    2. Intermediate
                    3. Advanced

                    Return valid JSON matching the ProjectRecommendationResponse schema.

                    The top-level fields MUST be:
                    - target_role
                    - recommendations

                    Use "recommendations", NOT "projects".

                    Each project must contain:
                    - project_name
                    - problem_statement (one concise sentence)
                    - difficulty
                    - skills_covered
                    - tech_stack
                    - milestones

                    All fields declared as lists in the schema must be JSON arrays,
                    never comma-separated strings.

                    Each project must have exactly 3 milestones. Each milestone must contain:
                    - order
                    - title
                    - description (one concise sentence)

                    Use existing candidate skills only when supported by the provided
                    information. Missing skills can be included as skills to learn.

                    Do not recommend generic chatbots, resume chatbots, PDF chatbots,
                    or basic document Q&A systems.

                    Avoid repeating the same skills across fields. Keep the details concise.
                    Generate all 3 projects and output JSON only.
                    """,
                ),
                (
                    "human",
                    """
                    Target role:
                    {target_role}

                    Existing matching skills:
                    {matching_skills}

                    Missing skills:
                    {missing_skills}

                    Transferable skills:
                    {transferable_skills}

                    Resume evidence:
                    {evidence}

                    Generate exactly 3 project recommendations as JSON.
                    """,
                ),
            ]
        )

        chain = project_recommendation_prompt | self.llm.bind(
            max_tokens=8192,
            reasoning_effort="low",
        ).with_structured_output(
            ProjectRecommendationResponse,
            method="json_schema",
            strict=True,
        )

        structured_response = chain.invoke(
            {
                "target_role": target_role,
                "matching_skills": ", ".join(matching_skills) or "None identified",
                "missing_skills": ", ".join(missing_skills) or "None identified",
                "transferable_skills": ", ".join(transferable_skills)
                or "None identified",
                "evidence": ", ".join(evidence) or "None identified",
            }
        )

        return structured_response
