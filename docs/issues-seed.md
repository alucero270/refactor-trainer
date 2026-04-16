# Issue Seed List

## M1 - Prompt and Heuristic Design

- `ISSUE-M1-1` Define heuristic thresholds for the MVP smell set.
- `ISSUE-M1-2` Prototype AST parsing and candidate segmentation for Python files.
- `ISSUE-M1-3` Design the classification prompt schema.
- `ISSUE-M1-4` Design the exercise prompt schema.
- `ISSUE-M1-5` Design the hint prompt schema and leakage guardrails.
- `ISSUE-M1-6` Curate the local guidance pack and rule-based snippet selection rules.

## M2 - Core Abstractions

- `ISSUE-M2-1` Define the `ModelProvider` contract.
- `ISSUE-M2-2` Define the provider configuration schema.
- `ISSUE-M2-3` Define the provider health model.
- `ISSUE-M2-4` Add a mock provider for early development.
- `ISSUE-M2-5` Define the `GuidanceRetriever` contract and fallback behavior.

## M3 - Ollama Provider

- `ISSUE-M3-1` Implement the Ollama provider.
- `ISSUE-M3-2` Add the provider health endpoint behavior for Ollama.
- `ISSUE-M3-3` Add an Ollama integration smoke test.

## M4 - Backend Core

- `ISSUE-M4-1` Set up the FastAPI project structure.
- `ISSUE-M4-2` Implement the `submit-code` endpoint.
- `ISSUE-M4-3` Implement parsing and deterministic candidate detection.
- `ISSUE-M4-4` Implement the `candidates` endpoint.
- `ISSUE-M4-5` Implement the `exercise` endpoint.
- `ISSUE-M4-6` Implement the `hints` endpoint.
- `ISSUE-M4-7` Implement the `submit-attempt` endpoint.
- `ISSUE-M4-8` Wire local guidance retrieval into generation flows.

## M5 - GitHub Targeted Import

- `ISSUE-M5-1` Implement the GitHub connection flow.
- `ISSUE-M5-2` Implement repository listing and file tree browsing endpoints.
- `ISSUE-M5-3` Import a selected GitHub file into the same `submit-code` pipeline.
- `ISSUE-M5-4` Add secret-safe GitHub token handling.

## M6 - BYOK Providers

- `ISSUE-M6-1` Implement the OpenAI provider.
- `ISSUE-M6-2` Implement the Anthropic provider.
- `ISSUE-M6-3` Add local secret-safe provider configuration storage.

## M7 - MCP Provider Integration

- `ISSUE-M7-1` Implement the MCP provider adapter.
- `ISSUE-M7-2` Add MCP config validation.
- `ISSUE-M7-3` Add MCP-specific error handling.
- `ISSUE-M7-4` Add MCP parity tests against the core provider contract.

## M8 - Frontend MVP

- `ISSUE-M8-1` Set up the React and TypeScript app structure.
- `ISSUE-M8-2` Build the provider setup UI.
- `ISSUE-M8-3` Build upload and paste ingestion UI.
- `ISSUE-M8-4` Build the GitHub import UI.
- `ISSUE-M8-5` Build the candidate list view.
- `ISSUE-M8-6` Build the exercise view and editor.
- `ISSUE-M8-7` Add attempt submission and feedback flow.

## M9 - Evaluation, Testing, and CI

- `ISSUE-M9-1` Implement deterministic evaluation logic.
- `ISSUE-M9-2` Add in-memory session management.
- `ISSUE-M9-3` Add structured logging and bounded metrics.
- `ISSUE-M9-4` Write backend unit tests.
- `ISSUE-M9-5` Write integration tests for the full exercise flow.
- `ISSUE-M9-6` Add schema validation tests for provider outputs.
- `ISSUE-M9-7` Add tests that fail if hints leak full solutions.
- `ISSUE-M9-8` Set up GitHub Actions CI.
