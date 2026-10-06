from typing import Any

from pydantic import BaseModel, Field


class OrchestratorRequest(BaseModel):
    message: str = Field(min_length=2, description="Natural-language career request")


class ToolExecutionResult(BaseModel):
    tool_name: str
    target_role: str | None = None
    success: bool
    output: Any | None = None
    error: str | None = None


class OrchestratorResponse(BaseModel):
    answer: str
    tools_called: list[str] = Field(default_factory=list)
    tool_results: list[ToolExecutionResult] = Field(default_factory=list)
