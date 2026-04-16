# ADR-0007: In-Memory Session Storage

## Status

Proposed

## Context

The MVP needs session continuity for one exercise loop, but persistent storage would add operational weight without proving the core product value.

## Decision

Use in-memory session storage for MVP and keep session data ephemeral.

## Consequences

- Positive: simple to implement and aligned with MVP speed
- Positive: privacy-friendly default posture
- Negative: state will not survive process restarts
- Negative: scaling and multi-instance support are deferred
