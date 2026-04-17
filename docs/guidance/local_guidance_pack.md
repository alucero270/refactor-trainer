# Local Guidance Pack

## Purpose

This document defines the MVP guidance sources that may be used during classification, exercise generation, and hint generation.

MVP guidance is fully local:

- all sources live in this repository
- no external retrieval system is required
- no network dependency is allowed

This document defines the source inventory and source-to-purpose mapping only.
It does not define snippet selection logic.

## Approved Local Sources

| Source | Path | Primary purpose |
| --- | --- | --- |
| Taxonomy | `docs/guidance/code_smell_taxonomy.md` | canonical smell labels, definitions, exclusions, and refactor direction |
| Difficulty rubric | `docs/guidance/difficulty_rubric.md` | difficulty calibration for classification and exercise outputs |
| Exercise authoring rules | `docs/guidance/exercise_authoring_rules.md` | constraints for exercise structure and learning boundary |
| Hint policy | `docs/guidance/hint_policy.md` | progressive hint behavior and anti-leak rules |
| Refactoring principles | `docs/guidance/refactoring_principles.md` | general maintainability and decomposition guidance |
| Good examples | `docs/guidance/examples/good_exercise_examples.md` | positive style examples for exercise framing |
| Bad examples | `docs/guidance/examples/bad_exercise_examples.md` | negative examples that show what to reject or avoid |

## Mapping By Output Type

### Classification

Required local sources:

- `docs/guidance/code_smell_taxonomy.md`
- `docs/guidance/difficulty_rubric.md`

Optional supporting source:

- `docs/guidance/refactoring_principles.md`

Classification must not depend on any external taxonomy, style guide, or hosted retrieval system.

### Exercise Generation

Required local sources:

- `docs/guidance/exercise_authoring_rules.md`
- `docs/guidance/difficulty_rubric.md`
- `docs/guidance/refactoring_principles.md`

Optional supporting sources:

- `docs/guidance/code_smell_taxonomy.md`
- `docs/guidance/examples/good_exercise_examples.md`
- `docs/guidance/examples/bad_exercise_examples.md`

### Hint Generation

Required local sources:

- `docs/guidance/hint_policy.md`
- `docs/guidance/code_smell_taxonomy.md`

Optional supporting sources:

- `docs/guidance/refactoring_principles.md`
- `docs/guidance/examples/good_exercise_examples.md`
- `docs/guidance/examples/bad_exercise_examples.md`

## Mapping By Guidance Concern

| Concern | Required source |
| --- | --- |
| Taxonomy | `docs/guidance/code_smell_taxonomy.md` |
| Rubric | `docs/guidance/difficulty_rubric.md` |
| Authoring rules | `docs/guidance/exercise_authoring_rules.md` |
| Hint policy | `docs/guidance/hint_policy.md` |

## Local-Only Rules

- Guidance content must be loaded from repository files only.
- Prompt construction must not require external documentation or online lookups.
- Missing optional sources must not block the flow.
- Any future non-local guidance source must be added through a separate architectural decision.

## Non-Goals

This document does not define:

- retrieval or ranking logic
- snippet limits
- fallback selection order
- Strata integration details
