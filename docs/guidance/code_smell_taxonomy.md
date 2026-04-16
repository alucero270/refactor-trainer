# Code Smell Taxonomy

This taxonomy is the authoritative smell vocabulary for MVP guidance and classification.

## MVP Detection Notes

Deterministic MVP candidate detection starts with:

- `LongMethod`
- `DeepNesting`
- `DuplicatedCode`
- `PoorNaming`

The taxonomy also includes `TooManyParameters` and `MixedResponsibility` so the guidance and prompt layer can stay stable as heuristic coverage grows.

## `LongMethod`

- Definition: A function exceeds reasonable size and performs multiple tasks.
- Why it matters: It is harder to read, test, and modify.
- Refactor direction: Extract functions and separate concerns.
- Do not flag: Long but linear data pipelines without meaningful branching or mixed responsibilities.
- Typical difficulty: Medium.

## `DeepNesting`

- Definition: Excessive nested conditionals or loops, typically more than two levels.
- Why it matters: It raises cognitive load and error risk.
- Refactor direction: Use guard clauses, early returns, or decomposition.
- Do not flag: Necessary domain logic with minimal real complexity.
- Typical difficulty: Medium.

## `DuplicatedCode`

- Definition: Repeated logic appears across blocks.
- Why it matters: It raises change risk and inconsistency risk.
- Refactor direction: Extract shared logic.
- Do not flag: Trivial repetition of one or two low-value lines.
- Typical difficulty: Easy to Medium.

## `PoorNaming`

- Definition: Variable or function names do not communicate intent.
- Why it matters: It slows comprehension.
- Refactor direction: Rename for clarity.
- Do not flag: Short names in very small scopes such as loop indices.
- Typical difficulty: Easy.

## `TooManyParameters`

- Definition: A function takes an excessive number of arguments.
- Why it matters: It is harder to reason about and use correctly.
- Refactor direction: Group parameters or extract objects.
- Do not flag: Small APIs where each parameter is necessary and still easy to reason about.
- Typical difficulty: Medium.

## `MixedResponsibility`

- Definition: A function or region handles unrelated concerns.
- Why it matters: It violates separation of concerns.
- Refactor direction: Split the work into cohesive units.
- Do not flag: Sequential work that remains part of one cohesive concern.
- Typical difficulty: Medium to Hard.
