

from langchain_core.prompts import ChatPromptTemplate

from schemas.careerAssessment_schema import InterviewCoachResult


class InterviewCoachAgent:
    def __init__(self, llm):

        self.llm = llm

    def analyze(
        self,
        target_role: str,
        resume_context: str,
        matching_skills: list[str],
        missing_skills: list[str],
        transferable_skills: list[str],
    ):
        interview_coach_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    You are an AI interview preparation coach.
                    Generate personalized interview questions for the
                    candidate and target role.
                    Rules:
                    1. Base questions only on the supplied resume,
                       role requirements, matching skills, missing skills,
                       and transferable skills.
                    2. Include questions covering:
                       - existing strengths
                       - resume projects
                       - target-role fundamentals
                       - missing-skill validation
                       - system design or practical problem solving
                    3. Do not assume experience not found in the resume.
                    4. Generate exactly:
                       - 3 beginner questions
                       - 4 intermediate questions
                       - 3 advanced questions
                    5. Interview questions must help the candidate prepare.
                       They must not make hiring or rejection decisions.
                    6. Provide a preparation hint, not a full answer.

                    Return your response strictly as valid JSON matching the InterviewCoachResult schema.
                    Do not include markdown, headings, or extra text.
                    """,
                ),
                (
                    "human",
                    """
                    Target role:
                    {target_role}
                    Candidate resume:
                    {resume_context}
                    Matching skills:
                    {matching_skills}
                    Missing skills:
                    {missing_skills}
                    Transferable skills:
                    {transferable_skills}
                    Generate the structured interview coaching plan.
                    """,
                ),
            ]
        )

        chain = interview_coach_prompt | self.llm
        response = chain.invoke(
            {
                "target_role": target_role,
                "resume_context": resume_context,
                "matching_skills": ", ".join(matching_skills) or "None identified",
                "missing_skills": ", ".join(missing_skills) or "None identified",
                "transferable_skills": ", ".join(transferable_skills)
                or "None identified",
            }
        )

        structured_llm = self.llm.with_structured_output(InterviewCoachResult)
        structured_response = structured_llm.invoke(response.content)

        return structured_response
