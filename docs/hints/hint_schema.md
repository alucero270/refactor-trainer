# Hint Schema Contract

## Purpose

This document defines the strict provider output contract for MVP hint generation.

The contract must enforce progressive behavior:

- Hint 1 orients the learner
- Hint 2 gives stronger structural guidance
- neither hint may reveal the solution

## Output Shape

Provider hint output must be a single JSON object with exactly these fields:

```json
{
  "hint_level": 1,
  "hint_type": "orientation",
  "hint": "Look at the order-processing branch where several responsibilities are interleaved and consider what one cohesive concern could be separated first."
}
```

## Strict Schema

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["hint_level", "hint_type", "hint"],
  "properties": {
    "hint_level": {
      "type": "integer",
      "enum": [1, 2]
    },
    "hint_type": {
      "type": "string",
      "enum": ["orientation", "guidance"]
    },
    "hint": {
      "type": "string",
      "minLength": 40,
      "maxLength": 240
    }
  }
}
```

## Level Rules

### Hint 1

- `hint_level` must be `1`
- `hint_type` must be `orientation`
- must identify the problematic region or concern
- must point in a general direction only
- must avoid naming a precise extraction or final structure

### Hint 2

- `hint_level` must be `2`
- `hint_type` must be `guidance`
- may suggest one structural strategy such as extraction or guard clauses
- may be more concrete than Hint 1, but must still stop short of the final answer
- must remain usable even if the learner has not yet chosen exact names or shapes

## Anti-Leak Rules

Hint output must not:

- include code blocks or inline refactored code
- provide a step-by-step implementation sequence
- prescribe exact helper names, class names, or final method layouts
- reveal all changes needed to finish the refactor
- expand the task beyond the selected issue

## Provider Stability Rules

- Output JSON only.
- Preserve field names and enum values exactly.
- Reject payloads with missing or extra fields.
- Reject payloads that violate progression or anti-leak rules even if they satisfy the JSON shape.

## Alignment Notes

This contract must stay aligned with:

- `docs/guidance/hint_policy.md`
- `docs/guidance/code_smell_taxonomy.md`
- the exercise schema that the hints build on
