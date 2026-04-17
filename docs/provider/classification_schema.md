# Classification Schema Contract

## Purpose

This document defines the strict provider output contract for candidate classification in MVP.

The contract is stable across all provider implementations and must match the approved taxonomy and difficulty rubric.

## Output Shape

Provider classification output must be a single JSON object with exactly these fields:

```json
{
  "label": "LongMethod",
  "rationale": "The candidate mixes several responsibilities and forces a reader to follow too much logic in one place.",
  "difficulty": "Medium"
}
```

## Strict Schema

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["label", "rationale", "difficulty"],
  "properties": {
    "label": {
      "type": "string",
      "enum": [
        "LongMethod",
        "DeepNesting",
        "DuplicatedCode",
        "PoorNaming",
        "TooManyParameters",
        "MixedResponsibility"
      ]
    },
    "rationale": {
      "type": "string",
      "minLength": 40,
      "maxLength": 400
    },
    "difficulty": {
      "type": "string",
      "enum": ["Easy", "Medium", "Hard"]
    }
  }
}
```

## Field Rules

### `label`

- Must match one taxonomy label exactly.
- Must represent one primary issue only.
- Must not invent synonyms or secondary labels.

### `rationale`

- Must explain why the issue matters in maintainability or readability terms.
- Must reference the candidate region, not the whole repository.
- Must not include refactored code, pseudo-code, or implementation steps.
- Must justify the selected label rather than merely restating it.

### `difficulty`

- Must align with the repo-local difficulty rubric.
- Must reflect the effort required to refactor the selected candidate, not the whole file.
- Must stay consistent with the taxonomy's typical difficulty unless the candidate clearly warrants a harder or easier rating.

## Difficulty Alignment Rules

Use these defaults unless candidate context clearly pushes the rating up or down:

| Label | Default difficulty | Allowed range |
| --- | --- | --- |
| `PoorNaming` | `Easy` | `Easy` |
| `DuplicatedCode` | `Easy` | `Easy`, `Medium` |
| `LongMethod` | `Medium` | `Medium`, `Hard` |
| `DeepNesting` | `Medium` | `Medium`, `Hard` |
| `TooManyParameters` | `Medium` | `Medium` |
| `MixedResponsibility` | `Hard` | `Medium`, `Hard` |

## Provider Stability Rules

- Output JSON only.
- Do not emit markdown, prose wrappers, or comments.
- Preserve field names exactly as written here.
- Reject any payload with missing fields or extra fields.

## Non-Goals

This contract does not define:

- candidate ranking
- parser thresholds
- exercise generation
- hint generation
