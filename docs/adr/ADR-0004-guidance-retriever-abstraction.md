# ADR-0004: Guidance Retriever Abstraction

## Status

Proposed

## Context

Output quality is MVP-critical, but the product must not couple itself to a future Strata implementation before that integration exists.

## Decision

Introduce a `GuidanceRetriever` abstraction that uses local rule-based guidance retrieval in MVP and preserves a future seam for a Strata-backed retriever.

## Consequences

- Positive: keeps prompt construction stable while the guidance source evolves
- Positive: preserves future Strata compatibility without forcing MVP transport work
- Negative: the initial retriever remains intentionally simple and non-semantic
- Negative: retrieval quality depends on disciplined local guidance authoring
