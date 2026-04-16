# ADR-0003: Provider Abstraction

## Status

Proposed

## Context

The MVP must support multiple model backends without spreading provider-specific logic throughout the codebase.

## Decision

Require every model backend to implement one `ModelProvider` contract for health checks, candidate classification, exercise generation, and hint generation.

## Consequences

- Positive: keeps core product logic provider-agnostic
- Positive: makes Ollama, OpenAI, Anthropic, and MCP interchangeable at the application boundary
- Negative: provider feature differences must be normalized to the lowest common contract
- Negative: schema enforcement and adapter maintenance become mandatory work
