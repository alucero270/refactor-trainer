from app.providers.base import ModelProvider


class OpenAIProvider(ModelProvider):
    kind = "remote"
    supports_local = False

    def name(self) -> str:
        return "openai"

    def healthCheck(self) -> dict:
        return {"provider": self.name(), "status": "stub", "message": "BYOK OpenAI integration not yet wired."}

    def classifyCandidate(self, payload: dict) -> dict:
        return {"provider": self.name(), "stage": "classification", "result": "stub", "input": payload}

    def generateExercise(self, payload: dict) -> dict:
        return {"provider": self.name(), "stage": "exercise", "result": "stub", "input": payload}

    def generateHints(self, payload: dict) -> dict:
        return {"provider": self.name(), "stage": "hints", "result": "stub", "input": payload}

