# ADR-0008: JSON Schema-Bound Provider Outputs

## Status

Proposed

## Context

Provider output quality will vary, and the MVP depends on predictable classification, exercise, and hint payloads.

## Decision

Require provider-generated outputs to conform to strict JSON schemas for each generation step.

## Consequences

- Positive: makes multi-provider support manageable
- Positive: reduces ambiguity in downstream orchestration
- Negative: invalid provider output must be rejected or retried
- Negative: prompt design and schema evolution need discipline
