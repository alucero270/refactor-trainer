# Contributing to Refactor Trainer

Refactor Trainer follows disciplined, structured development.

This repository is not a sandbox. Changes must align with:

* architecture
* MVP scope
* execution rules

---

## Core Principles

* single-file scope (MVP)
* deterministic analysis first
* AI assists, does not decide
* provider abstraction is required
* guidance rules must be enforced

---

## Contribution Workflow

1. Select or create a GitHub issue
2. Confirm scope is clear
3. Implement the smallest valid change
4. Validate against acceptance criteria
5. Submit PR

---

## Scope Definitions

All work must map to one of the following scopes:

* parser
* provider
* guidance
* exercise
* hints
* evaluation
* api
* frontend
* github
* storage
* testing
* docs
* infra

Do not introduce new scopes.

---

## Type Definitions

Use one of:

* feat
* fix
* refactor
* test
* docs
* chore

---

## Commit Message Guidelines

type(scope): description

Examples:

feat(parser): add function length detection
feat(provider): add ollama classification call
fix(hints): prevent solution leakage

---

## Pull Request Requirements

Each PR must:

* reference an issue
* stay within scope
* not introduce architectural drift
* pass validation checks

---

## Testing Strategy

* heuristic logic must be tested
* evaluation must be deterministic
* AI output must follow schema
* hints must not reveal solutions

---

## What NOT to Do

* do not expand beyond MVP scope
* do not add multi-file analysis
* do not bypass provider abstraction
* do not introduce platform features
* do not over-engineer

---

## Decision Rule

If something is unclear:

→ choose the simplest valid implementation
→ do not expand scope
→ do not invent behavior
→ ask questions if needed, do not assume

---

## Final Rule

Correct structure is more important than feature completeness.
