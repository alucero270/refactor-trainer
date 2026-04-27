import json
from urllib import error as urllib_error
from urllib import request as urllib_request

from pydantic import BaseModel

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
from app.providers.json_schema import strict_json_schema
from app.providers.prompts import classification_prompt, exercise_prompt, hint_prompt
from app.storage.memory import app_state


class AnthropicProviderError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


class AnthropicProvider(ModelProvider):
    kind = "remote"
    supports_local = False
    anthropic_version = "2023-06-01"
    default_base_url = "https://api.anthropic.com/v1"
    default_model = "claude-sonnet-4-6"

    def name(self) -> str:
        return "anthropic"

    def healthCheck(self) -> ProviderHealth:
        try:
            model_name = self._resolve_model_name()
            self._validate_model_available(model_name)
        except AnthropicProviderError as exc:
            return ProviderHealth(
                provider=self.name(),
                status="unavailable",
                available=False,
                message="Anthropic is unavailable.",
                failure=ProviderFailure(code=exc.code, detail=exc.detail),
            )

        return ProviderHealth(
            provider=self.name(),
            status="ready",
            available=True,
            message=f"Anthropic is ready with model '{model_name}'.",
        )

    def classifyCandidate(
        self, payload: CandidateClassificationInput
    ) -> CandidateClassificationResult:
        response = self._generate_json(
            classification_prompt(payload),
            tool_name="candidate_classification",
            result_type=CandidateClassificationResult,
        )
        return CandidateClassificationResult.model_validate(response)

    def generateExercise(
        self, payload: ExerciseGenerationInput
    ) -> ExerciseGenerationResult:
        response = self._generate_json(
            exercise_prompt(payload),
            tool_name="exercise_generation",
            result_type=ExerciseGenerationResult,
        )
        return ExerciseGenerationResult.model_validate(response)

    def generateHints(self, payload: HintGenerationInput) -> HintGenerationResult:
        response = self._generate_json(
            hint_prompt(payload),
            tool_name="hint_generation",
            result_type=HintGenerationResult,
        )
        return HintGenerationResult.model_validate(response)

    def _generate_json(
        self,
        prompt: str,
        *,
        tool_name: str,
        result_type: type[BaseModel],
    ) -> dict:
        response = self._request_json(
            "POST",
            "/messages",
            {
                "model": self._resolve_model_name(),
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}],
                "tools": [
                    {
                        "name": tool_name,
                        "description": "Return the requested Refactor Trainer JSON payload.",
                        "input_schema": strict_json_schema(result_type),
                    }
                ],
                "tool_choice": {"type": "tool", "name": tool_name},
            },
        )
        return self._extract_tool_input(response, tool_name)

    def _validate_model_available(self, model_name: str) -> None:
        response = self._request_json("GET", "/models")
        models = response.get("data")
        if not isinstance(models, list):
            raise AnthropicProviderError(
                "invalid_response",
                "Anthropic models response did not include a data list.",
            )

        model_names = {
            model["id"].strip()
            for model in models
            if isinstance(model, dict)
            and isinstance(model.get("id"), str)
            and model["id"].strip()
        }
        if model_name not in model_names:
            raise AnthropicProviderError(
                "model_not_found",
                f"Configured Anthropic model '{model_name}' is not available.",
            )

    def _request_json(self, method: str, path: str, payload: dict | None = None) -> dict:
        api_key = self._api_key()
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib_request.Request(
            url=f"{self._base_url()}{path}",
            data=body,
            method=method,
            headers={
                "Accept": "application/json",
                "anthropic-version": self.anthropic_version,
                "Content-Type": "application/json",
                "x-api-key": api_key,
            },
        )
        try:
            with urllib_request.urlopen(request, timeout=10) as response:
                raw_body = response.read().decode("utf-8")
        except urllib_error.HTTPError as exc:
            code = "authentication_failed" if exc.code in {401, 403} else "http_error"
            raise AnthropicProviderError(
                code,
                f"Anthropic returned HTTP {exc.code} for {path}.",
            ) from exc
        except urllib_error.URLError as exc:
            raise AnthropicProviderError(
                "connection_error",
                "Could not reach Anthropic.",
            ) from exc

        try:
            parsed = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise AnthropicProviderError(
                "invalid_response",
                f"Anthropic returned invalid JSON for {path}.",
            ) from exc

        if not isinstance(parsed, dict):
            raise AnthropicProviderError(
                "invalid_response",
                f"Anthropic returned a non-object JSON payload for {path}.",
            )
        return parsed

    @staticmethod
    def _extract_tool_input(response: dict, tool_name: str) -> dict:
        content = response.get("content")
        if not isinstance(content, list):
            raise AnthropicProviderError(
                "invalid_response",
                "Anthropic response did not include content blocks.",
            )

        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") != "tool_use" or block.get("name") != tool_name:
                continue
            tool_input = block.get("input")
            if isinstance(tool_input, dict):
                return tool_input

        raise AnthropicProviderError(
            "invalid_response",
            "Anthropic response did not include the requested tool output.",
        )

    @staticmethod
    def _api_key() -> str:
        api_key = app_state.provider_config.providers.anthropic.api_key
        if api_key is None or not api_key.get_secret_value().strip():
            raise AnthropicProviderError(
                "missing_api_key",
                "Anthropic API key is required for BYOK provider access.",
            )
        return api_key.get_secret_value()

    def _resolve_model_name(self) -> str:
        configured_model = app_state.provider_config.providers.anthropic.model
        if configured_model and configured_model.strip():
            return configured_model.strip()
        return self.default_model

    def _base_url(self) -> str:
        configured_base_url = app_state.provider_config.providers.anthropic.base_url
        base_url = configured_base_url.strip() if configured_base_url else self.default_base_url
        return base_url.rstrip("/")
