from langchain_core.prompts import ChatPromptTemplate

from schemas.gapAnalysis_schema import GapAnalysis


class GapAnalysisAgent:
    def __init__(self, llm):
        self.llm = llm

    def analyze_gap(self, resume_context: str, job_context: str):
        prompt = ChatPromptTemplate.from_template(
            """
            Compare candidate skills
            with target role requirements.
            
            Candidate Profile:
            {resume_context}
            
            Job Requirements:
            {job_context}
            
            Identify:
            1. Matching skills
            2. Missing skills
            3. Recommendation
            """
        )

        chain = prompt | self.llm
        response = chain.invoke(
            {"resume_context": resume_context, "job_context": job_context}
        )

        structured_llm = self.llm.with_structured_output(GapAnalysis)
        structured_response = structured_llm.invoke(response.content)

        return structured_response
