# Hint Policy

## Hint Levels

### Hint 1 - Orientation

Hint 1 should:

- identify the problematic region
- highlight the design issue
- suggest a general direction

### Hint 2 - Guidance

Hint 2 should:

- suggest a specific strategy such as extraction or guard clauses
- provide structural guidance without providing the final implementation

## Hard Rules

Hints must:

- never output full code
- never provide step-by-step implementation
- never reveal the final structure completely

## Enforcement

If a generated hint violates these rules, the system should strip or replace it rather than passing it through unchanged.
