# Guidance Retrieval Rules

## Purpose

This document defines MVP retrieval behavior for selecting local guidance snippets during classification, exercise generation, and hint generation.

These rules are design-only and must remain compatible with the `GuidanceRetriever` seam described in the architecture docs.

## Selection Rules

### General Rules

- Select snippets from repo-local guidance files only.
- Prefer the smallest set of snippets that satisfies the current generation step.
- Prefer snippets that map directly to the current output type and selected issue.
- Do not load full documents when a smaller relevant excerpt is sufficient.
- Do not select example snippets unless the primary rules documents are insufficient on their own.

### Classification Selection

Use this priority order:

1. matching taxonomy label definition
2. taxonomy exclusion notes for closely related labels
3. difficulty rubric guidance when the rating is ambiguous

### Exercise Selection

Use this priority order:

1. exercise authoring rules
2. difficulty rubric guidance
3. refactoring principles relevant to the selected issue
4. example snippets only when needed to clarify acceptable phrasing

### Hint Selection

Use this priority order:

1. hint policy
2. taxonomy guidance for the selected issue
3. refactoring principles only when needed to suggest a non-leaky direction
4. example snippets only when needed to show acceptable tone, not solution content

## Max Snippet Constraints

### Count Limits

- Classification: at most `2` snippets
- Exercise generation: at most `3` snippets
- Hint generation: at most `2` snippets

### Size Limits

- Each snippet should be no more than `12` lines.
- Combined snippet payload for one generation step should be no more than `36` lines.
- When a rule can be summarized safely in fewer lines, prefer the shorter excerpt.

### Relevance Limits

- Do not include duplicate snippets with overlapping guidance.
- Do not include both good and bad examples in the same prompt unless a rule document alone is genuinely insufficient.
- Do not include snippets unrelated to the selected issue type or output step.

## Fallback Behavior

Fallback must never block generation.

When ideal retrieval is not available:

1. use the smallest required baseline source set for the generation step
2. omit optional supporting snippets
3. continue generation with the local baseline guidance

Baseline fallback sets:

- Classification: taxonomy snippet plus difficulty rubric snippet
- Exercise generation: exercise authoring rules plus difficulty rubric snippet
- Hint generation: hint policy snippet plus taxonomy snippet

If no targeted issue-specific snippet can be selected:

- use the closest general rule from the required baseline set
- continue without examples
- do not fail the request solely because retrieval quality is reduced

## Decoupling Rules

- Retrieval rules must not assume Strata storage, embeddings, or hosted indexing.
- Retrieval rules must not depend on transport-specific metadata.
- Any future Strata-backed retriever must conform to these prompt-shaping rules rather than redefining them.

## Non-Goals

This document does not define:

- parser heuristics
- provider schemas
- semantic search
- external retrieval services
