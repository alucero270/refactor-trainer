# Exercise Schema Contract

## Purpose

This document defines the strict provider output contract for MVP exercise generation.

The contract must preserve the learning boundary:

- one primary issue only
- rationale is required
- no full solution output is allowed

## Output Shape

Provider exercise output must be a single JSON object with exactly these fields:

```json
{
  "title": "Reduce responsibility overlap in an order-processing function",
  "description": "Refactor this region so the main flow is easier to follow and the responsibilities are more cohesive.",
  "rationale": "This candidate is hard to maintain because several concerns are mixed together, which makes changes riskier and comprehension slower.",
  "difficulty": "Medium"
}
```

## Strict Schema

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["title", "description", "rationale", "difficulty"],
  "properties": {
    "title": {
      "type": "string",
      "minLength": 12,
      "maxLength": 80
    },
    "description": {
      "type": "string",
      "minLength": 40,
      "maxLength": 280
    },
    "rationale": {
      "type": "string",
      "minLength": 40,
      "maxLength": 280
    },
    "difficulty": {
      "type": "string",
      "enum": ["Easy", "Medium", "Hard"]
    }
  }
}
```

## Field Rules

### `title`

- Must be concise and task-oriented.
- Must describe the improvement target, not the final implementation.
- Must avoid imperative solution language such as naming a required helper or final structure.

### `description`

- Must describe what to improve and where the learner should focus.
- Must stay scoped to the selected candidate region.
- Must not prescribe a step-by-step sequence.

### `rationale`

- Must explain why the refactor matters in maintainability, readability, or change-safety terms.
- Must connect back to the classified issue, not introduce a second primary issue.
- Must not reveal the finished design.

### `difficulty`

- Must align with the local difficulty rubric and classification difficulty for the same candidate.
- Must use only `Easy`, `Medium`, or `Hard`.

## No-Solution Rules

Exercise output must not:

- include refactored code
- describe a required final method or class layout
- prescribe exact extraction names
- give a complete ordered implementation plan
- expand into multiple major refactors beyond the chosen issue

## Provider Stability Rules

- Output JSON only.
- Preserve field names exactly.
- Reject payloads with missing fields or extra fields.
- Reject payloads that include solution leakage even if they are valid JSON.

## Alignment Notes

This contract must stay aligned with:

- `docs/guidance/exercise_authoring_rules.md`
- `docs/guidance/difficulty_rubric.md`
- the classification schema contract used earlier in the flow
