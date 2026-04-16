# AGENTS.md

---

## 1. Repo Layout

* `backend/`: FastAPI application scaffold, provider abstractions, guidance seam, tests
* `frontend/`: React + TypeScript application scaffold with Monaco editor placeholder
* `docs/`: architecture notes, API spec, ADRs, prompts, repo-local guidance content
* `.github/workflows/`: CI baseline

---

## 2. Run Commands

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

## 3. Test Commands

```bash
cd backend
pytest
```

```bash
cd frontend
npm run build
```

---

## 4. Core System Identity

Refactor Trainer is a:

* local-first developer tool
* guided refactoring practice system
* structured training loop for real-world code

It provides:

* deterministic code analysis (heuristics)
* structured exercise generation
* progressive hints (no full solutions)
* controlled AI usage via provider abstraction

---

## 5. Architecture Constraints

* Keep the system monolithic
* Backend: Python + FastAPI
* Frontend: React + TypeScript
* Use provider abstraction for all model interactions
* Treat Ollama as the reference local-first provider
* Keep OpenAI, Anthropic, and MCP as BYOK-compatible paths

---

## 6. Scaffold Constraints

* Prefer placeholder implementations over speculative product logic
* Preserve clean seams for:

  * provider abstraction
  * guidance retrieval
  * future MCP-backed integrations
* Do not prematurely optimize architecture

---

## 7. Execution Rules

* One issue = one isolated change
* Each issue must be independently reviewable
* Do not implement beyond the current issue scope
* Do not assume future features exist
* Do not combine multiple concerns into a single change

---

## 8. Priority Rules

When implementing:

1. Follow architecture exactly
2. Respect issue scope
3. Preserve abstraction boundaries
4. THEN implement functionality

Do not optimize for completeness over correctness.

---

## 9. AI Usage Rules

AI is used for:

* classification
* exercise generation
* hint generation

AI is NOT used for:

* evaluation decisions (must be deterministic)
* system design decisions
* inventing requirements

All AI interactions must go through the provider abstraction.

---

## 10. Guidance Rules

* Exercises must target a single refactor issue
* Hints must NOT reveal full solutions
* Hints must be progressive (level 1 → level 2)
* Outputs must align with guidance documents
* Avoid generic or vague explanations

---

## 11. Provider Rules

* All model usage must go through provider abstraction
* No direct API calls in domain logic
* Do not couple system behavior to a specific provider
* Provider implementations may be stubbed in scaffold phase

---

## 12. GitHub Integration Rules

* GitHub is used for file ingestion only
* Do not implement:

  * repository sync
  * PR automation
  * background polling
* Keep integration minimal and scoped to file import

---

## 13. Validation Expectations

* Code must run successfully
* API contracts must remain stable
* Evaluation logic must be deterministic
* No placeholder logic may appear as complete implementation

---

## 14. Testing Policy

* Core logic should be tested
* Heuristics must be validated
* AI outputs must be schema-validated
* Hint leakage (solutions) must be prevented

---

## 15. Failure Handling

If an issue cannot be completed:

* stop execution immediately
* do not modify unrelated code
* do not expand scope
* do not attempt silent recovery
* surface the failure clearly

---

## 16. Do-Not-Overbuild Rules

* Do not implement full GitHub OAuth or repository sync
* Do not implement real provider SDK calls in scaffold phase
* Do not implement real MCP transport in scaffold phase
* Do not build cross-file or repository-wide analysis
* Do not add hosted/shared inference
* Do not add collaboration, accounts, or gamification
* Do not tightly couple guidance retrieval to Strata
* Do not fabricate deep logic in tests

---

## 17. UNATTENDED MODE (EXPERIMENTAL)

UNATTENDED MODE allows the agent to execute multiple issues sequentially without human review between issues.

This mode is **NOT default behavior**.

---

### 17.1 Purpose

To evaluate whether the agent can:

* follow structured plans
* maintain architectural boundaries
* produce correct incremental work
* operate without supervision

---

### 17.2 Execution Model (Stacked PR Workflow)

When UNATTENDED MODE is enabled:

* A milestone is selected
* Issues are executed in strict order

Branch structure:

* `milestone/mX`
* `issue/mX-01`
* `issue/mX-02` (based on previous branch)
* `issue/mX-03` (based on previous branch)

PR targets:

* `issue/mX-01` → `milestone/mX`
* `issue/mX-02` → `issue/mX-01`
* `issue/mX-03` → `issue/mX-02`

---

### 17.3 Rules

* Each issue MUST build on the previous issue
* Do NOT skip issues
* Do NOT reorder execution
* Do NOT parallelize work
* Do NOT merge PRs automatically

---

### 17.4 Failure Behavior

If any issue fails:

* stop execution immediately
* do not proceed to next issue
* do not modify previous branches

---

### 17.5 Completion

When all issues are complete:

* leave full PR stack open
* do not merge anything automatically
* require human review for all PRs

---

### 17.6 Priority (UNATTENDED MODE)

Even in unattended execution:

1. Follow architecture
2. Respect issue boundaries
3. Maintain abstraction integrity
4. THEN implement functionality

---

## 18. Anti-Patterns (DO NOT DO)
Do not implement multi-file analysis
Do not introduce background workers or queues
Do not add persistent storage beyond session scope
Do not bypass provider abstraction
Do not generate full refactored solutions
Do not invent missing requirements
Do not overbuild UI or system components

---

## 19. Guiding Principle

Refactor Trainer improves how developers think, not how fast code is generated.