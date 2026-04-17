# MVP Heuristic Specification

## Purpose

This document defines the deterministic MVP smell heuristics for single-file Python analysis.

It is a design contract only:

- no parser implementation is implied here
- no provider behavior is defined here
- ranking rules are defined separately

## Global Rules

- Analysis unit: one Python function or method at a time.
- Candidate region: the smallest function or method body that satisfies a smell trigger.
- File scope: a single submitted Python file only.
- Count executable statements only. Ignore blank lines, comments, decorators, and the docstring-only statement when applying thresholds.
- Apply exclusions before emitting a candidate.

## `LongMethod`

### Trigger

Flag a function or method as `LongMethod` when either condition is true:

- executable statement count is `>= 18`
- non-blank, non-comment body line count is `>= 30`

### Supporting Signals

These signals strengthen the candidate but do not change the threshold:

- contains more than one branching construct
- mixes data preparation with I/O, formatting, or persistence calls
- uses three or more temporary variables across separate steps

### Exclusions

Do not flag `LongMethod` when any of the following apply:

- the function is primarily a linear mapping or orchestration pipeline with no nesting deeper than one level
- most of the counted lines are a single literal structure, such as a large dictionary or list definition
- the function is test data setup or fixture construction with descriptive naming and no branching

## `DeepNesting`

### Trigger

Flag a function or method as `DeepNesting` when:

- maximum nesting depth of control-flow blocks is `>= 3`

Count these as nesting blocks:

- `if` / `elif` / `else`
- `for`
- `while`
- `try` / `except`
- `with`
- `match`

### Notes

- `elif` increases depth because it extends the nested decision chain.
- Comprehensions do not count as nesting blocks for MVP.

### Exclusions

Do not flag `DeepNesting` when:

- the measured depth comes only from defensive wrappers such as one `try` plus one `with`
- nested blocks are confined to a short guard section of `<= 6` executable statements before an early return
- the depth is created by generated-style test scaffolding rather than business logic

## `DuplicatedCode`

### Trigger

Flag `DuplicatedCode` when the file contains at least two regions that satisfy all of the following:

- each region has `>= 5` executable lines
- normalized token sequence similarity is `>= 80%`
- the regions differ only by identifiers, literals, or attribute names

MVP duplicate comparison scope:

- sibling blocks inside one function
- separate functions in the same file

### Normalization Rules

For comparison purposes only:

- ignore comments and whitespace
- normalize local identifiers to placeholders
- normalize string and numeric literals to placeholders
- preserve control-flow keywords and call structure

### Exclusions

Do not flag `DuplicatedCode` when:

- the repeated region is `<= 2` executable lines
- the repetition is limited to logging, argument validation, or simple return wrappers
- the similar blocks represent required protocol methods whose shared abstraction would add more indirection than value in MVP

## `PoorNaming`

### Trigger

Flag `PoorNaming` when either condition is true within one candidate region:

- the function or method name is a generic term from the disallowed list
- two or more local identifiers in meaningful scope match a poor-name rule

Poor-name rules:

- identifier length is `<= 2` outside an allowed short-name context
- identifier matches a generic placeholder term

Disallowed generic terms:

- `data`
- `info`
- `item`
- `obj`
- `thing`
- `stuff`
- `tmp`
- `temp`
- `val`
- `var`
- `misc`
- `helper`

Meaningful scope means the identifier is used in at least one executable statement outside a loop header or parameter list only.

### Exclusions

Do not flag `PoorNaming` when:

- the short name is a conventional loop index such as `i`, `j`, or `k`
- the short name is a standard coordinate or math symbol such as `x`, `y`, or `n` in a compact local calculation
- the identifier is a common callback convention such as `fn`, `cb`, `db`, or `id` and its purpose stays clear from the immediate context

## Output Expectations

Each emitted heuristic candidate should be able to point to:

- the smell label
- the triggering function or method
- the threshold that was crossed
- any exclusion check that was considered and not matched

## Non-Goals

This spec does not define:

- ranking or tie-breaking
- AST node models
- provider prompts
- runtime remediation behavior
