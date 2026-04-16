# Architecture

## Summary

Refactor Trainer remains a monolithic MVP: a React + TypeScript frontend, a FastAPI backend, deterministic analysis services, a provider abstraction, and a guidance retrieval seam. The architecture is intentionally local-first, keeps BYOK remote providers optional, treats MCP as a full provider path, and limits GitHub support to targeted single-file import.

## Architectural Goals

- Keep the MVP monolithic and easy to ship.
- Do as much work as possible deterministically before calling a provider.
- Treat Ollama as the reference local-first provider path.
- Keep OpenAI, Anthropic, and MCP behind the same provider contract.
- Route GitHub imports into the same single-file ingestion path as upload and paste.
- Keep guidance retrieval local in MVP while preserving a future Strata-compatible seam.

## System Components

### Frontend

The frontend is responsible for:

- provider setup and health checking
- upload, paste, and GitHub import entry points
- candidate list presentation
- exercise display
- progressive hint reveal
- in-app code editing and attempt submission
- feedback presentation

### Backend API

The backend owns:

- session orchestration
- code ingestion and normalization
- parsing and deterministic candidate detection
- provider-backed classification, exercise generation, and hint generation
- attempt evaluation
- provider configuration and diagnostics
- targeted GitHub file import

### Deterministic Analysis Layer

The deterministic layer handles:

- input normalization
- AST parsing
- code segmentation
- candidate detection
- baseline ranking
- completion checks

This keeps provider usage bounded and preserves predictable behavior when provider quality varies.

### Guidance Layer

The MVP guidance layer reads local docs only. It supplies small, relevant snippets to prompts for:

- taxonomy-backed classification
- exercise authoring constraints
- hint policy enforcement
- difficulty calibration

This layer must stay decoupled from any Strata-specific transport or storage.

### Provider Layer

All providers implement the same internal contract. Core exercise logic must not import provider-specific SDKs directly.

```ts
interface ModelProvider {
  name(): string;
  healthCheck(): Promise<ProviderHealth>;
  classifyCandidate(input: CandidateClassificationInput): Promise<CandidateClassificationResult>;
  generateExercise(input: ExerciseGenerationInput): Promise<ExerciseGenerationResult>;
  generateHints(input: HintGenerationInput): Promise<HintGenerationResult>;
}
```

Supported MVP provider paths:

- `OllamaProvider`
- `OpenAIProvider`
- `AnthropicProvider`
- `McpProvider`

### Guidance Retrieval Seam

The planning contract for guidance retrieval is:

```ts
interface GuidanceRetriever {
  getGuidance(input: {
    language: string;
    issueType?: string;
    difficulty?: string;
    query: string;
    maxSnippets: number;
  }): Promise<GuidanceSnippet[]>;
}
```

MVP behavior:

- source: local repo guidance docs only
- selection: rule-based, not embeddings-based
- fallback: minimal baseline guidance, never block exercise generation

Future Strata work must conform to this seam rather than reshaping prompt contracts.

## End-to-End MVP Flow

1. The user configures a provider.
2. The user uploads code, pastes code, or imports a single Python file from GitHub.
3. The backend normalizes the code and parses it to AST.
4. Deterministic heuristics identify 2-3 candidate refactors.
5. The selected provider classifies a candidate and produces rationale.
6. The exercise generation flow retrieves local guidance snippets.
7. The selected provider generates one exercise brief.
8. The selected provider generates two progressive hints on demand.
9. The user edits code in-app and submits an attempt.
10. Deterministic checks return pass/fail feedback and lightweight metadata.

## GitHub Import Boundary

GitHub support is an ingestion feature, not a repository analysis feature. MVP GitHub behavior is limited to:

- connecting a GitHub account or integration path
- listing accessible repositories
- browsing a repository tree
- importing one selected file
- passing imported content into the same single-file workflow used by upload and paste

Out of scope for MVP:

- repository-wide analysis
- branch workflows
- pull request workflows
- cross-file reasoning
- repository synchronization

## Storage Model

MVP storage stays intentionally small:

- session state: in-memory
- provider configuration and secrets: local-device scoped
- guidance content: repo-local markdown docs

This preserves the local-first posture and keeps the scaffold simple.

## Deployment Posture

The recommended deployment shape is a Dockerized single-service backend with a separately served frontend. This preserves simplicity while leaving room for later packaging or self-hosted deployment options.

## Deferred By Design

Deferred beyond MVP:

- repository-scale indexing
- cross-file reasoning
- hosted shared inference paid by the product owner
- automatic provider routing or fallback
- gamification
- collaboration features
- Strata-backed retrieval implementation
- real MCP transport orchestration beyond the provider seam
