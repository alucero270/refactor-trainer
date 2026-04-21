import json
from itertools import count
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
from app.storage.memory import app_state


class McpProviderError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


class McpProvider(ModelProvider):
    kind = "mcp"
    supports_local = False
    protocol_version = "2025-06-18"
    classify_tool = "refactor_trainer.classify_candidate"
    exercise_tool = "refactor_trainer.generate_exercise"
    hint_tool = "refactor_trainer.generate_hints"

    def __init__(self) -> None:
        self._request_ids = count(1)

    def name(self) -> str:
        return "mcp"

    def healthCheck(self) -> ProviderHealth:
        try:
            tools = self._list_tool_names()
            missing_tools = sorted(self._required_tools() - tools)
            if missing_tools:
                raise McpProviderError(
                    "missing_tools",
                    f"MCP server is missing required tools: {', '.join(missing_tools)}.",
                )
        except McpProviderError as exc:
            return ProviderHealth(
                provider=self.name(),
                status="unavailable",
                available=False,
                message="MCP provider is unavailable.",
                failure=ProviderFailure(code=exc.code, detail=exc.detail),
            )

        return ProviderHealth(
            provider=self.name(),
            status="ready",
            available=True,
            message="MCP provider is ready.",
        )

    def classifyCandidate(
        self, payload: CandidateClassificationInput
    ) -> CandidateClassificationResult:
        response = self._call_tool(
            self.classify_tool,
            payload.model_dump(mode="json"),
            result_type=CandidateClassificationResult,
        )
        return CandidateClassificationResult.model_validate(response)

    def generateExercise(
        self, payload: ExerciseGenerationInput
    ) -> ExerciseGenerationResult:
        response = self._call_tool(
            self.exercise_tool,
            payload.model_dump(mode="json"),
            result_type=ExerciseGenerationResult,
        )
        return ExerciseGenerationResult.model_validate(response)

    def generateHints(self, payload: HintGenerationInput) -> HintGenerationResult:
        response = self._call_tool(
            self.hint_tool,
            payload.model_dump(mode="json"),
            result_type=HintGenerationResult,
        )
        return HintGenerationResult.model_validate(response)

    def _list_tool_names(self) -> set[str]:
        response = self._json_rpc("tools/list", {})
        result = self._result(response)
        tools = result.get("tools")
        if not isinstance(tools, list):
            raise McpProviderError(
                "invalid_response",
                "MCP tools/list response did not include a tools list.",
            )
        return {
            tool["name"].strip()
            for tool in tools
            if isinstance(tool, dict)
            and isinstance(tool.get("name"), str)
            and tool["name"].strip()
        }

    def _call_tool(
        self,
        tool_name: str,
        arguments: dict,
        *,
        result_type: type[BaseModel],
    ) -> dict:
        response = self._json_rpc(
            "tools/call",
            {
                "name": tool_name,
                "arguments": {
                    "input": arguments,
                    "output_schema": strict_json_schema(result_type),
                },
            },
            mcp_name=tool_name,
        )
        result = self._result(response)
        if result.get("isError") is True:
            raise McpProviderError(
                "tool_error",
                f"MCP tool '{tool_name}' reported an error.",
            )

        structured_content = result.get("structuredContent")
        if isinstance(structured_content, dict):
            return structured_content

        content_text = self._content_text(result)
        return self._parse_json_object(content_text, tool_name)

    def _json_rpc(
        self,
        method: str,
        params: dict,
        *,
        mcp_name: str | None = None,
    ) -> dict:
        request_id = next(self._request_ids)
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params,
        }
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
            "MCP-Protocol-Version": self.protocol_version,
            "Mcp-Method": method,
        }
        if mcp_name is not None:
            headers["Mcp-Name"] = mcp_name

        request = urllib_request.Request(
            url=self._server_url(),
            data=body,
            method="POST",
            headers=headers,
        )
        try:
            with urllib_request.urlopen(request, timeout=10) as response:
                raw_body = response.read().decode("utf-8")
        except urllib_error.HTTPError as exc:
            raise McpProviderError(
                "http_error",
                f"MCP server returned HTTP {exc.code} for {method}.",
            ) from exc
        except urllib_error.URLError as exc:
            raise McpProviderError(
                "connection_error",
                "Could not reach MCP server.",
            ) from exc

        try:
            parsed = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise McpProviderError(
                "invalid_response",
                f"MCP server returned invalid JSON for {method}.",
            ) from exc

        if not isinstance(parsed, dict):
            raise McpProviderError(
                "invalid_response",
                f"MCP server returned a non-object JSON payload for {method}.",
            )
        if parsed.get("id") != request_id:
            raise McpProviderError(
                "invalid_response",
                f"MCP server returned a mismatched response id for {method}.",
            )
        return parsed

    @staticmethod
    def _result(response: dict) -> dict:
        if "error" in response:
            raise McpProviderError(
                "json_rpc_error",
                "MCP server returned a JSON-RPC error response.",
            )

        result = response.get("result")
        if not isinstance(result, dict):
            raise McpProviderError(
                "invalid_response",
                "MCP response did not include a result object.",
            )
        return result

    @staticmethod
    def _content_text(result: dict) -> str:
        content = result.get("content")
        if not isinstance(content, list):
            raise McpProviderError(
                "invalid_response",
                "MCP tool response did not include content blocks.",
            )

        text_parts = [
            block["text"]
            for block in content
            if isinstance(block, dict)
            and block.get("type") == "text"
            and isinstance(block.get("text"), str)
        ]
        joined = "".join(text_parts).strip()
        if not joined:
            raise McpProviderError(
                "invalid_response",
                "MCP tool response did not include text content.",
            )
        return joined

    @staticmethod
    def _parse_json_object(raw_response: str, tool_name: str) -> dict:
        try:
            payload = json.loads(raw_response)
        except json.JSONDecodeError as exc:
            raise McpProviderError(
                "invalid_response",
                f"MCP tool '{tool_name}' response did not contain valid JSON.",
            ) from exc

        if not isinstance(payload, dict):
            raise McpProviderError(
                "invalid_response",
                f"MCP tool '{tool_name}' response did not contain a JSON object.",
            )
        return payload

    @classmethod
    def _required_tools(cls) -> set[str]:
        return {cls.classify_tool, cls.exercise_tool, cls.hint_tool}

    @staticmethod
    def _server_url() -> str:
        server_url = app_state.provider_config.providers.mcp.server_url
        if server_url is None or not server_url.strip():
            raise McpProviderError(
                "missing_server_url",
                "MCP server_url is required for provider access.",
            )
        return server_url.strip()
