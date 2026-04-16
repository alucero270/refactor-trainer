# ADR-0002: Local-First Provider Strategy

## Status

Proposed

## Context

Refactor Trainer is intended to help developers practice on real code while staying cost-conscious and privacy-aware. The product needs a clear default provider posture for MVP.

## Decision

Make local-first the default strategy and treat Ollama as the reference provider path for MVP. Support remote providers only as optional BYOK alternatives.

## Consequences

- Positive: reinforces privacy and cost control
- Positive: gives the MVP a clear product identity
- Negative: local model quality may vary by user environment
- Negative: provider setup becomes part of the onboarding burden
