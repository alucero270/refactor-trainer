# ADR-0005: GitHub Targeted Import

## Status

Proposed

## Context

Using real code improves product usefulness, but full repository analysis would push the MVP beyond a disciplined scope.

## Decision

Include GitHub connection and targeted single-file import in MVP, and route imported content into the same single-file ingestion path as upload and paste.

## Consequences

- Positive: lowers friction for practicing on real code
- Positive: keeps GitHub support useful without turning it into repository analysis
- Negative: adds auth and import edge cases to the MVP
- Negative: users may still expect broader repository features that are out of scope
