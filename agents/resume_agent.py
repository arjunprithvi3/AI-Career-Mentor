from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from schemas.resume_schema import ResumeSchema


class ResumeAnalysisAgent:

    def __init__(self,llm,retriever):
        self.llm = llm
        self.retriever = retriever

    def analyze_resume(self):

        prompt = ChatPromptTemplate.from_template(
            """
            Analyze the resume.

            Resume Context:
            {context}

            Extract:

            1. Skills
            2. Experience Years
            3. Projects
            4. Education

            Return the information according to the provided schema.
            """
            )


        document_chain = create_stuff_documents_chain(self.llm,prompt)
        retrieval_chain = create_retrieval_chain(self.retriever,document_chain)
        response = retrieval_chain.invoke(
            {
                "input":"Analyse the complete resume"
            }
        )

        structured_llm = self.llm.with_structured_output(ResumeSchema)
        structured_response = structured_llm.invoke(
            response["answer"]
        )

        return structured_response


      

