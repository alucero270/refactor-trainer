# Hint Policy

## Hint Levels

### Hint 1 - Orientation

Hint 1 should:

- identify the problematic region
- highlight the design issue
- suggest a general direction
- avoid naming the exact final structure

### Hint 2 - Guidance

Hint 2 should:

- suggest a specific strategy such as extraction or guard clauses
- provide structural guidance without providing the final implementation
- stay consistent with, but more specific than, Hint 1

## Hard Rules

Hints must:

- never output full code
- never provide step-by-step implementation
- never reveal the final structure completely
- never prescribe exact helper or class names
- never combine multiple major refactors into one hint

## Enforcement

If a generated hint violates these rules, the system should strip or replace it rather than passing it through unchanged.

## Output Contract Expectations

- Hint output must identify whether it is level 1 or level 2.
- Hint 1 must use orientation-style guidance.
- Hint 2 must use stronger structural guidance.
- Both hint levels must remain inside the selected candidate scope.
