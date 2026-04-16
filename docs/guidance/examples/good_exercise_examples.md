# Good Exercise Examples

## Example 1 - Long Method

Candidate:

- `LongMethod`
- Function mixes iteration, filtering, and transformation.

Exercise:

> Refactor this function to improve readability and reduce responsibility overlap. Focus on making the main flow easier to understand without changing what the function does.

Why this is good:

- targets one primary issue
- explains the improvement goal
- does not prescribe a single final structure
- does not reveal implementation

## Example 2 - Deep Nesting

Candidate:

- `DeepNesting`
- Several nested conditionals make the main path hard to follow.

Exercise:

> Refactor this logic to reduce cognitive load in the heavily nested region. Aim to make the decision flow easier to read and safer to modify.

Why this is good:

- keeps scope narrow
- ties the task to readability and change risk
- leaves room for more than one valid approach

## Example 3 - Poor Naming

Candidate:

- `PoorNaming`
- Variable and helper names obscure intent.

Exercise:

> Refine the naming in this region so that the purpose of the values and operations is obvious to a future reader.

Why this is good:

- stays focused on the selected smell
- avoids cosmetic churn outside the target issue
- frames the improvement in engineering terms
