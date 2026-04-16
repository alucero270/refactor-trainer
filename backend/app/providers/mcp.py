from app.providers.base import ModelProvider


class McpProvider(ModelProvider):
    kind = "mcp"
    supports_local = False

    def name(self) -> str:
        return "mcp"

    def healthCheck(self) -> dict:
        return {"provider": self.name(), "status": "stub", "message": "MCP transport is intentionally not implemented yet."}

    def classifyCandidate(self, payload: dict) -> dict:
        return {"provider": self.name(), "stage": "classification", "result": "stub", "input": payload}

    def generateExercise(self, payload: dict) -> dict:
        return {"provider": self.name(), "stage": "exercise", "result": "stub", "input": payload}

    def generateHints(self, payload: dict) -> dict:
        return {"provider": self.name(), "stage": "hints", "result": "stub", "input": payload}

