# Product Scope

## Problem

Refactor Trainer exists for developers who rely heavily on AI coding assistance and want to keep their refactoring instincts sharp. The product focuses on real maintainability practice instead of algorithm drills or direct code generation.

## Intended Users

Primary users:

- professional developers who worry their design instincts are dulling
- working engineers who want deliberate refactoring practice on realistic code
- developers preparing for interviews

Secondary users:

- team leads looking for structured junior practice
- self-taught developers who want stronger maintainability instincts

## Product Definition

Refactor Trainer is a lightweight tool that:

- ingests a snippet, single file, or targeted GitHub-imported file
- detects refactor candidates
- explains why a candidate matters
- generates one guided exercise
- reveals hints progressively
- lets the user attempt the refactor without receiving the full answer

It is not:

- a code generator
- a LeetCode-style platform
- a generic tutorial system
- a social product
- a marketplace

## Why It Exists

General LLM workflows tend to jump to answers. Static analysis tools flag issues but do not teach. Traditional coding platforms focus on puzzles rather than production maintainability. Refactor Trainer fills that gap with a deliberate practice loop centered on real code.

## Competitive Framing

| Alternative | Strength | Gap relative to this product | Refactor Trainer angle |
| --- | --- | --- | --- |
| LeetCode | Strong interview prep and algorithms | Not about maintainability or personal code | Practice on realistic refactoring targets |
| Codewars | Broad challenge format | External kata and gamified framing | Turn your own code into exercises |
| Exercism | Mentoring and idiomatic guidance | Mentor-dependent and curated | Automated personalized practice |
| Copilot / chat workflows | Fast assistance | Encourages passive acceptance and direct solutions | Guided practice without answer leakage |
| Static analysis tools | Reliable issue detection | No teaching loop | Convert warnings into exercises |

## Capability Classification

| Capability | Classification | Notes |
| --- | --- | --- |
| Single-file upload or paste | MVP | Simplest useful entry point |
| Targeted GitHub file import | MVP | Alternate ingestion path into the same workflow |
| Deterministic candidate detection | MVP | Reliable baseline before provider calls |
| Provider-backed classification | MVP | Adds rationale and learning context |
| Exercise brief generation | MVP | Core product value |
| Difficulty scoring | MVP | Helps prioritization |
| Progressive hints | MVP | Preserves challenge |
| Attempt recording and evaluation | MVP | Completes the practice loop |
| Provider setup and health checks | MVP | Required for local-first and BYOK support |
| Ollama provider path | MVP | Default local-first path |
| OpenAI BYOK | MVP | Optional remote path |
| Anthropic BYOK | MVP | Optional remote path |
| MCP provider path | MVP | First-class provider support behind abstraction |
| Full repository analysis | Post-MVP | Explicitly outside MVP |
| Cross-file reasoning | Post-MVP | Explicitly outside MVP |
| Broader language support | Post-MVP | MVP targets Python |
| Full solution generation | Post-MVP | Conflicts with the learning goal |
| Collaboration and sharing | Post-MVP | Not part of the MVP wedge |
| Gamification and leaderboards | Cut for MVP | Scope distraction |
| Hosted shared inference paid by the product owner | Cut for MVP | Conflicts with local-first and cost control |

## Strategic Boundaries

- Local-first is the default posture.
- BYOK remote providers are optional, not the center of the MVP.
- MCP is preserved as a full provider path, not a separate orchestration product.
- Guidance retrieval stays local in MVP, with a future seam for Strata compatibility.
- GitHub support stays targeted to single-file import and must not expand into repository-wide analysis.
