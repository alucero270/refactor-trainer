# Testing Strategy

## Testing Goals

The MVP test strategy must prove that:

- deterministic analysis behaves predictably
- provider-backed generation stays inside strict JSON schemas
- hints do not leak final solutions
- targeted GitHub import behaves like any other ingestion source
- the local-first, BYOK, and MCP seams remain stable

## Principles

- Prefer small, deterministic tests over fabricated deep-logic tests.
- Contract-test abstractions so provider implementations can vary safely.
- Use fixtures and mocked provider responses for repeatability.
- Validate behavior that preserves the learning boundary, not just happy-path transport.

## Test Layers

### Unit Tests

Cover:

- AST parsing and syntax-failure handling
- candidate detection heuristics
- candidate ranking logic
- attempt evaluation logic
- local guidance retrieval selection and fallback
- secret-safe config handling

### Contract Tests

Cover:

- `ModelProvider` interface compliance for Ollama, OpenAI, Anthropic, and MCP
- JSON schema validation for classification, exercise, and hint outputs
- `GuidanceRetriever` contract compliance and fallback behavior

### Integration Tests

Cover:

- full backend exercise flow from `/submit-code` through `/submit-attempt/{exercise_id}`
- provider config and health endpoints
- GitHub repository browsing and single-file import
- session continuity during the active exercise flow

### Smoke Tests

Cover:

- Ollama end-to-end path as the reference implementation
- frontend build success
- service health endpoint

## Guidance and Prompt Validation

Tests must verify that:

- classification output aligns with the taxonomy
- exercise output respects authoring rules
- hint output respects hint policy
- difficulty labels align with the rubric
- retrieved guidance is actually incorporated into generation inputs

## Leakage and Safety Tests

Tests must fail when:

- a hint includes full refactored code
- a prompt response breaks the required JSON schema
- submitted code is executed instead of parsed
- secrets appear in logs
- remote-provider fallback happens automatically after local-provider failure

## Regression Fixtures

Maintain fixtures for:

- representative Python files up to the MVP size range
- common smell cases
- false-positive edge cases
- GitHub-imported file payloads
- provider schema failure cases

## CI Expectations

CI should run:

- backend unit and integration tests
- provider and guidance contract tests
- schema validation tests
- frontend build

The CI goal is diagnosis as much as correctness: failures should clearly indicate whether the break came from heuristics, prompt/schema alignment, provider behavior, GitHub import, or session handling.
