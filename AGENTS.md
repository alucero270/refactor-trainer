# AGENTS.md

---

## Source of Truth

Before making structural or architectural changes, consult:

* docs/architecture.md
* docs/mvp-definition.md
* docs/product-scope.md
* docs/adr/
* CONTRIBUTING.md

If AGENTS.md conflicts with these documents:

→ stop execution
→ surface the conflict
→ do not resolve it independently

---

## Repo Layout

* `backend/`: backend application, core logic, providers, tests
* `frontend/`: UI application and interaction flow
* `docs/`: architecture, ADRs, API spec, prompts, guidance
* `.github/workflows/`: CI configuration

---

## Run Commands

### Backend

```bash
cd backend
python -m pip install -e .
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Test Commands

```bash
cd backend
pytest
```

```bash
cd frontend
npm run build
```

---

## Execution Rules

* One issue = one isolated change
* Each issue must be independently reviewable
* Do not implement beyond the current issue scope
* Do not assume future features exist
* Do not combine multiple concerns into a single change

---

## Priority Rules

When implementing:

1. Respect issue scope
2. Preserve existing abstractions
3. Follow architecture and ADRs
4. THEN implement functionality

Do not optimize for completeness over correctness.

---

## Implementation Rules

* Do not introduce new frameworks, services, or architectural patterns without approval
* Do not change public interfaces or contracts without explicit instruction
* Do not bypass defined abstractions
* Prefer the smallest valid implementation
* Surface ambiguity rather than inventing behavior

---

## AI Usage Rules

AI may be used for:

* classification
* exercise generation
* hint generation

AI must NOT be used for:

* deterministic evaluation decisions
* architecture decisions
* inventing requirements

All AI usage must respect defined abstractions.

---

## Guidance Rules

* Exercises must target a single refactor issue
* Hints must NOT reveal full solutions
* Hints must be progressive
* Outputs must align with guidance documents
* Avoid generic or vague explanations

---

## Validation Rules

* Code must run successfully
* Changes must align with issue acceptance criteria
* Tests must reflect implemented logic
* No placeholder logic may appear as complete implementation

---

## Testing Rules

* Test deterministic system behavior, not user experience
* Validate logic within issue scope
* Ensure interfaces remain stable
* Enforce constraints (no leakage, no unsafe execution)

Do not fabricate misleading tests.

---

## Failure Handling

If an issue cannot be completed:

* stop execution immediately
* do not modify unrelated code
* do not expand scope
* do not attempt silent recovery
* surface the failure clearly

---

## Do-Not-Overbuild Rules

* Do not expand beyond MVP scope
* Do not introduce undefined features
* Do not add platform features (accounts, collaboration, etc.)
* Do not introduce background workers or queues
* Do not add unnecessary infrastructure
* Do not tightly couple external systems prematurely
* Do not over-engineer

---

## UNATTENDED MODE (EXPERIMENTAL)

UNATTENDED MODE allows the agent to execute multiple issues sequentially without human review.

This mode is **disabled by default** and must be explicitly enabled.

---

### Purpose

To evaluate whether the agent can:

* follow structured plans
* respect issue boundaries
* maintain abstraction integrity
* produce correct incremental changes
* detect and stop on failure

---

## Execution Loop

For a selected milestone:

For each issue, in strict order:

1. Create a branch from the previous issue branch
2. Implement only the current issue
3. Run validation checks
4. If validation passes → open PR
5. If validation fails → stop execution

The agent MUST NOT proceed to the next issue unless validation passes.

---

## Branching Model

Branches:

* `milestone/mX`
* `issue/mX-01`
* `issue/mX-02` (from previous issue branch)
* `issue/mX-03` (from previous issue branch)

PR targets:

* `issue/mX-01` → `milestone/mX`
* `issue/mX-02` → `issue/mX-01`
* `issue/mX-03` → `issue/mX-02`

---

## Validation Gate (MANDATORY)

Before opening a PR, ALL must pass:

### 1. Build & Runtime

* backend starts successfully
* frontend builds successfully (if affected)

### 2. Tests

* all existing tests pass
* new tests (if required) pass

### 3. Scope Enforcement

* changes match issue scope
* no unrelated files modified
* no future features introduced

### 4. Contract Integrity

* API contracts preserved unless required
* abstractions not bypassed

### 5. Safety Constraints

* no execution of user code
* no hint solution leakage
* no secrets exposed

If ANY check fails:

→ stop execution

---

## PR Requirements (UNATTENDED)

Each PR must:

* reference exactly one issue
* include only relevant changes
* follow `type(scope): description` naming
* pass all validation gates

PR description must include:

* issue reference
* summary of changes
* confirmation that validation passed

---

## Failure Classification

If execution fails, classify as:

* BUILD_FAILURE
* TEST_FAILURE
* SCOPE_VIOLATION
* CONTRACT_VIOLATION
* SAFETY_VIOLATION
* UNKNOWN

Then:

* stop execution
* do not proceed
* do not modify previous branches

---

## Stop Conditions

Execution MUST stop if:

* validation fails
* scope is unclear
* dependency is missing
* architecture conflict detected
* contracts cannot be satisfied

Do NOT:

* skip issues
* expand scope
* partially complete work

---

## Completion Behavior

When all issues are complete:

* leave full PR stack open
* do NOT merge automatically
* require human review

---

## Execution Constraints

* Do NOT skip issues
* Do NOT reorder execution
* Do NOT parallelize work
* Do NOT merge PRs automatically

---

## Priority (UNATTENDED MODE)

1. Respect issue scope
2. Pass validation
3. Preserve abstractions
4. Follow architecture docs
5. THEN implement

---

## Expected Output Quality

Each issue must result in:

* one clean branch
* one focused PR
* no scope drift
* no speculative code
* no hidden coupling

---

## Anti-Patterns (DO NOT DO)

* Invent missing requirements
* Expand scope implicitly
* Bypass system boundaries
* Introduce unrelated changes
* Replace structured logic with AI output

---

## Guiding Principle

Correct structure and disciplined execution matter more than feature completeness.
