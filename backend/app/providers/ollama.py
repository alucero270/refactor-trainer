from app.providers.base import ModelProvider


class OllamaProvider(ModelProvider):
    kind = "local"
    supports_local = True

    def name(self) -> str:
        return "ollama"

    def healthCheck(self) -> dict:
        return {"provider": self.name(), "status": "stub", "message": "Local Ollama path not yet wired."}

    def classifyCandidate(self, payload: dict) -> dict:
        return {"provider": self.name(), "stage": "classification", "result": "stub", "input": payload}

    def generateExercise(self, payload: dict) -> dict:
        return {"provider": self.name(), "stage": "exercise", "result": "stub", "input": payload}

    def generateHints(self, payload: dict) -> dict:
        return {"provider": self.name(), "stage": "hints", "result": "stub", "input": payload}

