# ADR-0006: MCP as Full MVP Provider Path

## Status

Proposed

## Context

The product direction must preserve MCP compatibility, but MCP work cannot be allowed to reshape the MVP into a general orchestration platform.

## Decision

Keep MCP as a full MVP provider path behind the same provider abstraction as Ollama, OpenAI, and Anthropic.

## Consequences

- Positive: preserves extensibility and future compatibility
- Positive: avoids branching core logic for MCP-specific flows
- Negative: MCP config and diagnostics add MVP complexity
- Negative: parity expectations increase testing and validation burden
