import json
from urllib import error as urllib_error
from urllib import request as urllib_request

from app.providers.base import ModelProvider
from app.providers.contracts import (
    CandidateClassificationInput,
    CandidateClassificationResult,
    ExerciseGenerationInput,
    ExerciseGenerationResult,
    HintGenerationInput,
    HintGenerationResult,
    ProviderFailure,
    ProviderHealth,
)
from app.storage.memory import app_state


class OllamaProviderError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


class OllamaProvider(ModelProvider):
    kind = "local"
    supports_local = True

    def name(self) -> str:
        return "ollama"

    def healthCheck(self) -> ProviderHealth:
        try:
            available_models = self._list_model_names()
            active_model = self._resolve_model_name(available_models)
        except OllamaProviderError as exc:
            return ProviderHealth(
                provider=self.name(),
                status="unavailable",
                available=False,
                message="Ollama is unavailable.",
                failure=ProviderFailure(code=exc.code, detail=exc.detail),
            )

        return ProviderHealth(
            provider=self.name(),
            status="ready",
            available=True,
            message=f"Ollama is ready with model '{active_model}'.",
        )

    def classifyCandidate(
        self, payload: CandidateClassificationInput
    ) -> CandidateClassificationResult:
        response = self._generate_json(
            self._classification_prompt(payload),
        )
        return CandidateClassificationResult.model_validate(response)

    def generateExercise(
        self, payload: ExerciseGenerationInput
    ) -> ExerciseGenerationResult:
        response = self._generate_json(
            self._exercise_prompt(payload),
        )
        return ExerciseGenerationResult.model_validate(response)

    def generateHints(self, payload: HintGenerationInput) -> HintGenerationResult:
        response = self._generate_json(
            self._hint_prompt(payload),
        )
        return HintGenerationResult.model_validate(response)

    def _generate_json(self, prompt: str) -> dict:
        model_name = self._resolve_model_name(self._list_model_names())
        response = self._request_json(
            "POST",
            "/api/generate",
            {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "format": "json",
            },
        )

        raw_response = response.get("response")
        if not isinstance(raw_response, str) or not raw_response.strip():
            raise OllamaProviderError(
                "invalid_response",
                "Ollama generate response did not include a JSON body.",
            )

        parsed = self._parse_json_object(raw_response)
        return parsed

    def _list_model_names(self) -> list[str]:
        payload = self._request_json("GET", "/api/tags")
        models = payload.get("models")
        if not isinstance(models, list):
            raise OllamaProviderError(
                "invalid_response",
                "Ollama tags response did not include a models list.",
            )

        model_names = [
            model["name"].strip()
            for model in models
            if isinstance(model, dict)
            and isinstance(model.get("name"), str)
            and model["name"].strip()
        ]
        if not model_names:
            raise OllamaProviderError(
                "no_models",
                "No Ollama models are available. Pull a model locally before using the provider.",
            )
        return model_names

    def _resolve_model_name(self, available_models: list[str]) -> str:
        configured_model = app_state.provider_config.providers.ollama.model
        if configured_model and configured_model.strip():
            normalized = configured_model.strip()
            if normalized not in available_models:
                raise OllamaProviderError(
                    "model_not_found",
                    f"Configured Ollama model '{normalized}' is not available locally.",
                )
            return normalized
        return available_models[0]

    def _request_json(self, method: str, path: str, payload: dict | None = None) -> dict:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib_request.Request(
            url=f"{app_state.provider_config.providers.ollama.base_url.rstrip('/')}{path}",
            data=body,
            method=method,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib_request.urlopen(request, timeout=5) as response:
                raw_body = response.read().decode("utf-8")
        except urllib_error.HTTPError as exc:
            raise OllamaProviderError(
                "http_error",
                f"Ollama returned HTTP {exc.code} for {path}.",
            ) from exc
        except urllib_error.URLError as exc:
            raise OllamaProviderError(
                "connection_error",
                f"Could not reach Ollama at {app_state.provider_config.providers.ollama.base_url}.",
            ) from exc

        try:
            parsed = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise OllamaProviderError(
                "invalid_response",
                f"Ollama returned invalid JSON for {path}.",
            ) from exc

        if not isinstance(parsed, dict):
            raise OllamaProviderError(
                "invalid_response",
                f"Ollama returned a non-object JSON payload for {path}.",
            )
        return parsed

    @staticmethod
    def _parse_json_object(raw_response: str) -> dict:
        trimmed = raw_response.strip()
        if trimmed.startswith("```"):
            lines = trimmed.splitlines()
            if len(lines) >= 3 and lines[0].startswith("```") and lines[-1].startswith("```"):
                trimmed = "\n".join(lines[1:-1]).strip()

        try:
            payload = json.loads(trimmed)
        except json.JSONDecodeError as exc:
            raise OllamaProviderError(
                "invalid_response",
                "Ollama generate response did not contain valid JSON.",
            ) from exc

        if not isinstance(payload, dict):
            raise OllamaProviderError(
                "invalid_response",
                "Ollama generate response did not contain a JSON object.",
            )
        return payload

    @staticmethod
    def _classification_prompt(payload: CandidateClassificationInput) -> str:
        guidance = OllamaProvider._guidance_block(payload.guidance_snippets)
        expected_label = payload.heuristic_label or "LongMethod"
        return (
            "You are classifying one refactor candidate for a refactoring practice app.\n"
            "Return only JSON with keys label and rationale.\n"
            f"The label should stay aligned with the heuristic label '{expected_label}' unless the"
            " candidate clearly suggests a more precise smell.\n"
            f"Language: {payload.language}\n"
            f"Candidate region: {payload.candidate_region}\n"
            f"Detection summary: {payload.detection_summary}\n"
            f"Candidate code:\n{payload.candidate_code}\n"
            f"{guidance}"
        )

    @staticmethod
    def _exercise_prompt(payload: ExerciseGenerationInput) -> str:
        guidance = OllamaProvider._guidance_block(payload.guidance_snippets)
        return (
            "You are writing one refactoring exercise.\n"
            "Return only JSON with keys title, description, and difficulty.\n"
            "Difficulty must be one of Easy, Medium, or Hard.\n"
            "Do not reveal final code.\n"
            f"Language: {payload.language}\n"
            f"Issue label: {payload.issue_label}\n"
            f"Candidate region: {payload.candidate_region}\n"
            f"Classification rationale: {payload.classification_rationale}\n"
            f"Candidate code:\n{payload.candidate_code}\n"
            f"{guidance}"
        )

    @staticmethod
    def _hint_prompt(payload: HintGenerationInput) -> str:
        guidance = OllamaProvider._guidance_block(payload.guidance_snippets)
        return (
            "You are writing one progressive refactoring hint.\n"
            "Return only JSON with the key hint.\n"
            "Do not reveal final code or a full step-by-step solution.\n"
            f"Language: {payload.language}\n"
            f"Hint level: {payload.hint_level}\n"
            f"Exercise title: {payload.exercise_title}\n"
            f"Exercise description: {payload.exercise_description}\n"
            f"Issue label: {payload.issue_label}\n"
            f"Candidate code:\n{payload.candidate_code}\n"
            f"{guidance}"
        )

    @staticmethod
    def _guidance_block(guidance_snippets: list[str]) -> str:
        if not guidance_snippets:
            return "Guidance: stay within the shared provider contract."
        return "Guidance:\n- " + "\n- ".join(guidance_snippets)
