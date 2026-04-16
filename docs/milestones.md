# Milestones

## Delivery Sequence

1. Design heuristics and prompt/schema contracts.
2. Define the provider and guidance retrieval abstractions.
3. Implement Ollama as the reference path.
4. Build backend parsing, detection, orchestration, and API flow.
5. Add GitHub targeted import into the single-file workflow.
6. Add OpenAI and Anthropic BYOK providers.
7. Add MCP as a full provider path.
8. Build the frontend MVP flow.
9. Add evaluation, testing, logging, and CI hardening.

## Milestone Plan

| ID | Name | Goal | Scope | Dependencies | Exit Criteria |
| --- | --- | --- | --- | --- | --- |
| `M1` | Prompt and Heuristic Design | Establish reliable heuristics and prompt/schema structure | Thresholds, taxonomy alignment, prompt contracts, fixtures, guidance pack curation | None | Stable heuristics and schema-ready prompt assets exist |
| `M2` | Core Abstractions | Define provider and guidance retrieval contracts | `ModelProvider`, `GuidanceRetriever`, config model, health model, mock provider | `M1` | Core app can run against mock provider and local guidance retrieval |
| `M3` | Ollama Provider | Deliver the local-first reference path | Ollama adapter, health check, end-to-end generation | `M2` | Full flow works through Ollama |
| `M4` | Backend Core | Implement parsing, detection, orchestration, and session flow | FastAPI app, ingestion, candidates, exercises, hints, attempt submission, in-memory session handling | `M1`, `M2` | Backend core flow is operational |
| `M5` | GitHub Targeted Import | Add GitHub connection and single-file import | GitHub auth/connect path, repository listing, tree browsing, file import into the same ingestion path | `M4` | A user can import one file from GitHub and continue through the normal workflow |
| `M6` | BYOK Providers | Add OpenAI and Anthropic support | Provider adapters, key config, switching, diagnostics | `M2`, `M4` | Both BYOK providers support the core flow |
| `M7` | MCP Provider Integration | Retain MCP as full MVP provider support | MCP adapter, config validation, error handling, parity tests | `M2`, `M4` | MCP works without changing core product logic and supports all core generation operations |
| `M8` | Frontend MVP | Build the complete practice flow UI | Provider setup, upload, paste, GitHub import, candidates, exercise, editor, feedback | `M3`, `M4`, `M5` | A user can complete one exercise loop from any supported ingestion path |
| `M9` | Evaluation, Testing, and CI | Stabilize and operationalize the MVP | Evaluation logic, logging, metrics, unit tests, integration tests, CI | `M3`-`M8` | CI is green and failures are diagnosable |

## Notes

- GitHub import is intentionally placed before remote-provider expansion because it materially improves usefulness without expanding the product into repository analysis.
- MCP remains in the MVP milestone plan because it is a required provider path, but it must stay behind the same abstraction as the other providers.
