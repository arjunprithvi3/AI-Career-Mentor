import json
from typing import Any

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, ToolMessage

from app.core import app_state
from schemas.orchestrator_schema import OrchestratorResponse, ToolExecutionResult
from tools.orchestrator import career_tools
from tools.prompt import ORCHESTRATOR_PROMPT


class CareerOrchestrator:
    def __init__(self):
        if app_state.llm is None:
            raise RuntimeError(
                "LLM is not initialized. Ensure "
                "initialize_app() runs during FastAPI startup."
            )
        self.agent = create_agent(
            model=app_state.llm,
            tools=career_tools,
            system_prompt=(ORCHESTRATOR_PROMPT),
            name="career_orchestrator",
            debug=False,
        )

    def invoke(self, user_message: str) -> OrchestratorResponse:
        cleaned_message = user_message.strip()
        if not cleaned_message:
            raise ValueError("User message cannot be empty.")
        result = self.agent.invoke(
            {"messages": [{"role": "user", "content": cleaned_message}]}
        )
        messages = result.get("messages", [])
        tool_results = self._extract_tool_results(messages)
        final_answer = self._extract_final_answer(messages)
        if not final_answer:
            final_answer = self._build_fallback_answer(tool_results)
        return OrchestratorResponse(
            answer=final_answer,
            tools_called=[item.tool_name for item in tool_results],
            tool_results=tool_results,
        )

    @staticmethod
    def _extract_tool_results(messages: list[Any]) -> list[ToolExecutionResult]:
        results = []
        for message in messages:
            if not isinstance(message, ToolMessage):
                continue
            try:
                payload = json.loads(message.content)
                results.append(
                    ToolExecutionResult(
                        tool_name=payload.get(
                            "tool_name", message.name or "unknown_tool"
                        ),
                        target_role=payload.get("target_role"),
                        success=payload.get("success", True),
                        output=payload.get("output"),
                        error=payload.get("error"),
                    )
                )
            except (json.JSONDecodeError, TypeError):
                results.append(
                    ToolExecutionResult(
                        tool_name=(message.name or "unknown_tool"),
                        target_role=None,
                        success=True,
                        output=message.content,
                        error=None,
                    )
                )
        return results

    @staticmethod
    def _extract_final_answer(messages: list[Any]) -> str:
        for message in reversed(messages):
            if not isinstance(message, AIMessage):
                continue
            content = message.content
            if isinstance(content, str):
                return content.strip()
            return json.dumps(content, default=str)
        return ""

    @staticmethod
    def _build_fallback_answer(tool_results: list[ToolExecutionResult]) -> str:
        successful_tools = [
            result.tool_name for result in tool_results if result.success
        ]
        failed_tools = [
            result.tool_name for result in tool_results if not result.success
        ]
        parts = []
        if successful_tools:
            parts.append("Completed: " + ", ".join(successful_tools) + ".")
        if failed_tools:
            parts.append("Unable to complete: " + ", ".join(failed_tools) + ".")
        if not parts:
            return "No career tools were called. Please provide a target role."
        return " ".join(parts)
