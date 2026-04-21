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
from app.storage.memory import app_state


class OpenAIProviderError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


class OpenAIProvider(ModelProvider):
    kind = "remote"
    supports_local = False
    default_base_url = "https://api.openai.com/v1"
    default_model = "gpt-5"

    def name(self) -> str:
        return "openai"

    def healthCheck(self) -> ProviderHealth:
        try:
            model_name = self._resolve_model_name()
            self._request_json("GET", f"/models/{model_name}")
        except OpenAIProviderError as exc:
            return ProviderHealth(
                provider=self.name(),
                status="unavailable",
                available=False,
                message="OpenAI is unavailable.",
                failure=ProviderFailure(code=exc.code, detail=exc.detail),
            )

        return ProviderHealth(
            provider=self.name(),
            status="ready",
            available=True,
            message=f"OpenAI is ready with model '{model_name}'.",
        )

    def classifyCandidate(
        self, payload: CandidateClassificationInput
    ) -> CandidateClassificationResult:
        response = self._generate_json(
            self._classification_prompt(payload),
            schema_name="candidate_classification",
            result_type=CandidateClassificationResult,
        )
        return CandidateClassificationResult.model_validate(response)

    def generateExercise(
        self, payload: ExerciseGenerationInput
    ) -> ExerciseGenerationResult:
        response = self._generate_json(
            self._exercise_prompt(payload),
            schema_name="exercise_generation",
            result_type=ExerciseGenerationResult,
        )
        return ExerciseGenerationResult.model_validate(response)

    def generateHints(self, payload: HintGenerationInput) -> HintGenerationResult:
        response = self._generate_json(
            self._hint_prompt(payload),
            schema_name="hint_generation",
            result_type=HintGenerationResult,
        )
        return HintGenerationResult.model_validate(response)

    def _generate_json(
        self,
        prompt: str,
        *,
        schema_name: str,
        result_type: type[BaseModel],
    ) -> dict:
        response = self._request_json(
            "POST",
            "/responses",
            {
                "model": self._resolve_model_name(),
                "input": prompt,
                "store": False,
                "text": {
                    "format": {
                        "type": "json_schema",
                        "name": schema_name,
                        "strict": True,
                        "schema": self._strict_json_schema(result_type),
                    }
                },
            },
        )
        raw_output = self._extract_output_text(response)
        return self._parse_json_object(raw_output)

    @staticmethod
    def _strict_json_schema(result_type: type[BaseModel]) -> dict:
        schema = result_type.model_json_schema()
        schema["additionalProperties"] = False
        return schema

    def _request_json(self, method: str, path: str, payload: dict | None = None) -> dict:
        api_key = self._api_key()
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib_request.Request(
            url=f"{self._base_url()}{path}",
            data=body,
            method=method,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib_request.urlopen(request, timeout=10) as response:
                raw_body = response.read().decode("utf-8")
        except urllib_error.HTTPError as exc:
            code = "authentication_failed" if exc.code in {401, 403} else "http_error"
            if exc.code == 404 and path.startswith("/models/"):
                code = "model_not_found"
            raise OpenAIProviderError(
                code,
                f"OpenAI returned HTTP {exc.code} for {path}.",
            ) from exc
        except urllib_error.URLError as exc:
            raise OpenAIProviderError(
                "connection_error",
                "Could not reach OpenAI.",
            ) from exc

        try:
            parsed = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise OpenAIProviderError(
                "invalid_response",
                f"OpenAI returned invalid JSON for {path}.",
            ) from exc

        if not isinstance(parsed, dict):
            raise OpenAIProviderError(
                "invalid_response",
                f"OpenAI returned a non-object JSON payload for {path}.",
            )
        return parsed

    @staticmethod
    def _extract_output_text(response: dict) -> str:
        output_text = response.get("output_text")
        if isinstance(output_text, str) and output_text.strip():
            return output_text

        output = response.get("output")
        if isinstance(output, list):
            texts: list[str] = []
            for item in output:
                if not isinstance(item, dict):
                    continue
                content = item.get("content")
                if not isinstance(content, list):
                    continue
                for content_item in content:
                    if not isinstance(content_item, dict):
                        continue
                    text = content_item.get("text")
                    if isinstance(text, str):
                        texts.append(text)
            joined = "".join(texts).strip()
            if joined:
                return joined

        raise OpenAIProviderError(
            "invalid_response",
            "OpenAI response did not include output text.",
        )

    @staticmethod
    def _parse_json_object(raw_response: str) -> dict:
        try:
            payload = json.loads(raw_response.strip())
        except json.JSONDecodeError as exc:
            raise OpenAIProviderError(
                "invalid_response",
                "OpenAI response did not contain valid JSON.",
            ) from exc

        if not isinstance(payload, dict):
            raise OpenAIProviderError(
                "invalid_response",
                "OpenAI response did not contain a JSON object.",
            )
        return payload

    @staticmethod
    def _classification_prompt(payload: CandidateClassificationInput) -> str:
        guidance = OpenAIProvider._guidance_block(payload.guidance_snippets)
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
        guidance = OpenAIProvider._guidance_block(payload.guidance_snippets)
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
        guidance = OpenAIProvider._guidance_block(payload.guidance_snippets)
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

    @staticmethod
    def _api_key() -> str:
        api_key = app_state.provider_config.providers.openai.api_key
        if api_key is None or not api_key.get_secret_value().strip():
            raise OpenAIProviderError(
                "missing_api_key",
                "OpenAI API key is required for BYOK provider access.",
            )
        return api_key.get_secret_value()

    def _resolve_model_name(self) -> str:
        configured_model = app_state.provider_config.providers.openai.model
        if configured_model and configured_model.strip():
            return configured_model.strip()
        return self.default_model

    def _base_url(self) -> str:
        configured_base_url = app_state.provider_config.providers.openai.base_url
        base_url = configured_base_url.strip() if configured_base_url else self.default_base_url
        return base_url.rstrip("/")
