from agents.orchestrator_agent import CareerOrchestrator
from schemas.orchestrator_schema import OrchestratorResponse


class CareerOrchestratorService:
    def __init__(self):
        self.orchestrator = CareerOrchestrator()

    def process(self, message: str) -> OrchestratorResponse:
        return self.orchestrator.invoke(user_message=message)
