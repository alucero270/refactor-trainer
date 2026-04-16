# Difficulty Rubric

## Easy

Use `Easy` when the refactor is mostly local and low-ambiguity.

Typical signs:

- local change surface
- minimal design ambiguity
- limited sequencing decisions

Typical examples:

- rename variables for clarity
- perform a small extraction

## Medium

Use `Medium` when the refactor changes structure and requires judgment.

Typical signs:

- meaningful structural change
- some design tradeoffs
- one or two sequencing decisions

Typical examples:

- split a function
- reduce nesting with guard clauses
- group related parameters

## Hard

Use `Hard` when the refactor is multi-step and requires careful sequencing.

Typical signs:

- multiple coordinated changes
- high design ambiguity
- responsibility boundaries need reorganization

Typical examples:

- reorganize mixed responsibilities
- sequence several extractions to reduce coupling
