# MVP Definition

## Exact MVP Feature Set

1. Submit a single Python file by upload, paste, or targeted GitHub import.
2. Configure a provider before generation.
3. Parse and segment the code.
4. Detect 2-3 refactor candidates using deterministic heuristics.
5. Classify candidates with the selected provider.
6. Generate one exercise brief with rationale and difficulty.
7. Reveal two progressive hints.
8. Allow in-app editing and attempt submission.
9. Evaluate the attempt with simple deterministic checks.
10. Keep the guidance system local, rule-based, and compatible with a future Strata-backed retriever seam.

## What the User Can Do

- choose a provider
- upload code, paste code, or import one Python file from GitHub
- inspect ranked candidates
- open one exercise
- reveal hints in order
- submit a refactoring attempt
- receive pass/fail feedback

## Success Criteria

The MVP is successful when:

- one end-to-end exercise loop works reliably
- Ollama works as the default reference path
- OpenAI and Anthropic work through BYOK configuration
- MCP supports the same core generation operations as other providers
- GitHub import works as an alternate ingestion source into the same single-file flow
- guidance retrieval uses local docs without blocking the flow if retrieval falls back

## Explicit MVP Exclusions

The MVP must exclude:

- full repository-scale analysis
- cross-file reasoning
- repository synchronization
- branch, commit, or pull request workflows
- user accounts beyond what GitHub import requires
- collaboration
- gamification
- hosted shared inference
- automatic provider routing or fallback
- provider quality scoring
- full solution generation
- real MCP transport expansion beyond the provider path
- Strata-backed retrieval implementation

## Non-Negotiable Boundaries

- Local-first is the default posture.
- BYOK remains configuration-based.
- GitHub import remains targeted and single-file only.
- GuidanceRetriever remains a seam for future Strata compatibility.
- The app teaches refactoring; it does not hand over the finished answer.
