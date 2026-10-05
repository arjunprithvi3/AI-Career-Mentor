from langchain_core.prompts import ChatPromptTemplate

from schemas.careerAssessment_schema import JobFitAnalysis


class JobFitAgent:
    def __init__(self, llm):
        self.llm = llm

    def analyze(self, target_role: str, resume_context: str, job_context: str):
        jobfit_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
        	You are a career-fit analysis assistant.
        	Compare the candidate resume context against the
        	target job requirements.
        	Use only the supplied contexts. Do not invent
        	candidate skills, experience, or evidence.
        	Return one valid JSON object matching exactly this
        	structure:
        	{{
            	"role": "string",
            	"matching_skills": ["string"],
            	"missing_skills": ["string"],
            	"transferable_skills": ["string"],
            	"evidence": ["string"],
            	"suitability_summary": "string"
        	}}
        	JSON output rules:
        	1. Return valid JSON only.
        	2. Do not use Markdown code fences.
        	3. Do not add explanations outside the JSON object.
        	4. Use empty JSON arrays when no values are found.
        	5. Every matching skill must have support in the
           	supplied resume context.
        	""",
                ),
                (
                    "human",
                    """
        	Target role:
        	{target_role}
        	Candidate resume context:
        	{resume_context}
        	Job requirements context:
        	{job_context}
        	Produce the career-fit analysis as valid JSON.
        	""",
                ),
            ]
        )

        structured_llm = self.llm.with_structured_output(
            JobFitAnalysis, method="json_mode"
        )
        chain = jobfit_prompt | structured_llm
        return chain.invoke(
            {
                "target_role": target_role,
                "resume_context": resume_context,
                "job_context": job_context,
            }
        )
