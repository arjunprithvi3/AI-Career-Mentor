from langchain.agents import create_agent
from langchain_core.tools import StructuredTool

from app.core import app_state
from schemas.orchestrator_schema import OrchestratorResponse
from tools.orchestrator import career_tools
from tools.prompt import ORCHESTRATOR_PROMPT


class CareerOrchestrator:
    def __init__(self):

        if app_state.llm is None:
            raise RuntimeError(
                "LLM is not initialized. Ensure the "
                "FastAPI lifespan calls initialize_app()."
            )

        # --------------------------------------------------
        # Agent 1: Career orchestration + career tools
        # --------------------------------------------------

        self.agent = create_agent(
            model=app_state.llm,
            tools=career_tools,
            system_prompt=ORCHESTRATOR_PROMPT,
        )

        # --------------------------------------------------
        # Final Pydantic response tool
        # --------------------------------------------------

        def submit_response(**kwargs):
            response = OrchestratorResponse.model_validate(kwargs)
            return response.model_dump()

        self.response_tool = StructuredTool.from_function(
            func=submit_response,
            name="submit_orchestrator_response",
            description=(
                "Submit the final career response. "
                "This tool must be called after completing "
                "the required career analysis."
            ),
            args_schema=OrchestratorResponse,
        )

        # --------------------------------------------------
        # Agent 2: Final structured response
        # --------------------------------------------------

        final_model = app_state.llm.bind(tool_choice="submit_orchestrator_response")

        self.final_agent = create_agent(
            model=final_model,
            tools=[self.response_tool],
            system_prompt="""
You are the final response formatter.

You receive the results produced by the career orchestration agent.

You MUST call the tool:

submit_orchestrator_response

Do not answer with normal text.

Do not return Markdown.

Do not explain your reasoning.

Put all final information inside the Pydantic response
required by submit_orchestrator_response.

Include only sections relevant to the user's request. Summarize tool results
concisely and do not repeat the same skills or details across sections. Keep
final_guidance to one or two sentences.

When resource_recommendations are included, every item must include
skill, title, provider, resource_type, level, url, and reason.
Copy each resource's reason from the tool results; do not omit it.
""",
        )

    def invoke(self, user_message: str):

        cleaned_message = user_message.strip()

        if not cleaned_message:
            raise ValueError("User message cannot be empty.")

        # --------------------------------------------------
        # STEP 1: Run career agent
        # --------------------------------------------------

        result = self.agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": cleaned_message,
                    }
                ]
            }
        )

        messages = result.get("messages", [])

        if not messages:
            raise ValueError("The career orchestrator returned no messages.")

        # Get the final message from Agent 1
        final_message = messages[-1].content

        # --------------------------------------------------
        # STEP 2: Pass result to final structured agent
        # --------------------------------------------------

        tool_results = "\n\n".join(
            str(message.content)
            for message in messages
            if getattr(message, "type", None) == "tool"
        )

        final_result = self.final_agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": f"""
User request:

{cleaned_message}

Career orchestration result:

Tool results:
{tool_results}

Orchestrator summary:
{final_message}

Create the final structured response.
You MUST call submit_orchestrator_response.
""",
                    }
                ]
            }
        )

        # --------------------------------------------------
        # STEP 3: Extract Pydantic tool call
        # --------------------------------------------------

        final_messages = final_result.get("messages", [])

        for message in reversed(final_messages):
            tool_calls = getattr(message, "tool_calls", [])

            for tool_call in tool_calls:
                if tool_call["name"] == "submit_orchestrator_response":
                    return OrchestratorResponse.model_validate(tool_call["args"])

        raise ValueError("The final agent did not return submit_orchestrator_response.")
