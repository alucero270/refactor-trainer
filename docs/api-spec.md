# API Spec

## Scope

This document defines the MVP HTTP contract for the current monolithic backend. It matches the scaffolded route layout and preserves the planning decisions from the living plan:

- single-file Python ingestion only
- provider setup before generation
- targeted GitHub import only
- session-scoped exercise flow
- no repository-wide analysis

All endpoints exchange JSON unless noted otherwise.

## Session and Config Model

- Session state may be tracked with a cookie-backed session identifier in MVP.
- Provider configuration is local-device scoped and must not be logged.
- GitHub access is scoped to repository browsing and single-file import for the active exercise flow.

## Endpoint Summary

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Service health |
| `POST` | `/submit-code` | Upload or paste Python code into the session |
| `GET` | `/candidates` | Return detected candidates for a submission |
| `POST` | `/exercise/{candidate_id}` | Generate or retrieve an exercise for one candidate |
| `GET` | `/hints/{exercise_id}` | Reveal the next available hints for an exercise |
| `POST` | `/submit-attempt/{exercise_id}` | Submit a refactored attempt |
| `GET` | `/providers` | List supported provider modes |
| `GET` | `/provider/config` | Read the current provider config |
| `PUT` | `/provider/config` | Save the current provider config |
| `GET` | `/provider/health` | Validate configured provider availability |
| `GET` | `/github/connect` | Start or represent the GitHub connection flow |
| `GET` | `/github/repos` | List accessible repositories |
| `GET` | `/github/repo/{repo_id}/tree` | Browse a repository tree for importable files |
| `POST` | `/github/import-file` | Import one file into the single-file workflow |

## Contracts

### `GET /health`

Response:

```json
{
  "status": "ok",
  "app": "refactor-trainer",
  "scaffold": true
}
```

Notes:

- `scaffold` may remain `true` until placeholder implementations are replaced.

### `POST /submit-code`

Request:

```json
{
  "source": "paste",
  "filename": "example.py",
  "code": "def example():\n    pass\n"
}
```

Rules:

- `source` must be one of `upload`, `paste`, or `github`.
- MVP accepts Python only.
- Invalid syntax should surface a user-facing error after parsing.

Response:

```json
{
  "submission_id": "sub-123",
  "candidate_count": 3,
  "status": "accepted"
}
```

### `GET /candidates`

Query parameters:

- `submission_id` (required)

Response:

```json
{
  "submission_id": "sub-123",
  "candidates": [
    {
      "id": "cand-1",
      "title": "Split a long function",
      "smell": "LongMethod",
      "summary": "This function mixes multiple responsibilities.",
      "severity": "medium"
    }
  ]
}
```

Rules:

- Return up to 3 candidates in MVP.
- Candidates should include line-aware metadata internally even if the scaffolded response is still minimal.

### `POST /exercise/{candidate_id}`

Path parameters:

- `candidate_id` (required)

Response:

```json
{
  "exercise_id": "ex-123",
  "candidate_id": "cand-1",
  "instructions": "Refactor this function to improve readability and reduce responsibility overlap.",
  "guidance_summary": "Use one primary issue and do not reveal the final structure.",
  "status": "generated"
}
```

Rules:

- Generate one exercise per selected candidate.
- The exercise must describe what to improve and why it matters.
- The exercise must not include final refactored code.

### `GET /hints/{exercise_id}`

Path parameters:

- `exercise_id` (required)

Response:

```json
{
  "exercise_id": "ex-123",
  "hints": [
    "Look at the region where responsibilities start to mix.",
    "Consider extracting one cohesive piece of work into a helper."
  ],
  "guidance_summary": "Hints must stay progressive and must not reveal full code.",
  "status": "generated"
}
```

Rules:

- Hint 2 must not be available before Hint 1.
- Hints must not output full code or step-by-step implementation.

### `POST /submit-attempt/{exercise_id}`

Path parameters:

- `exercise_id` (required)

Request:

```json
{
  "attempt_code": "def refactored_example():\n    pass\n"
}
```

Response:

```json
{
  "exercise_id": "ex-123",
  "accepted": true,
  "feedback": "The targeted issue was reduced and the code still parses.",
  "status": "evaluated"
}
```

Rules:

- MVP evaluation is deterministic and lightweight.
- The backend must never execute submitted code.

### `GET /providers`

Response:

```json
{
  "providers": [
    {
      "name": "ollama",
      "kind": "local",
      "supports_local": true
    }
  ]
}
```

Notes:

- The supported MVP provider set is Ollama, OpenAI, Anthropic, and MCP.

### `GET /provider/config`

Response:

```json
{
  "config": {
    "default_provider": "ollama",
    "configured_providers": ["ollama"],
    "providers": {
      "ollama": {
        "base_url": "http://localhost:11434",
        "model": null
      },
      "openai": {
        "api_key": null,
        "model": null,
        "base_url": null
      },
      "anthropic": {
        "api_key": null,
        "model": null,
        "base_url": null
      },
      "mcp": {
        "server_url": null,
        "model": null
      }
    }
  }
}
```

### `PUT /provider/config`

Request:

```json
{
  "config": {
    "default_provider": "ollama",
    "configured_providers": ["ollama", "openai"],
    "providers": {
      "ollama": {
        "base_url": "http://localhost:11434",
        "model": null
      },
      "openai": {
        "api_key": "**********",
        "model": "gpt-test",
        "base_url": null
      },
      "anthropic": {
        "api_key": null,
        "model": null,
        "base_url": null
      },
      "mcp": {
        "server_url": null,
        "model": null
      }
    }
  }
}
```

Response:

```json
{
  "config": {
    "default_provider": "ollama",
    "configured_providers": ["ollama", "openai"],
    "providers": {
      "ollama": {
        "base_url": "http://localhost:11434",
        "model": null
      },
      "openai": {
        "api_key": "**********",
        "model": "gpt-test",
        "base_url": null
      },
      "anthropic": {
        "api_key": null,
        "model": null,
        "base_url": null
      },
      "mcp": {
        "server_url": null,
        "model": null
      }
    }
  }
}
```

Rules:

- Secrets are local-only and must never appear in logs.
- Config updates must not imply automatic fallback between providers.
- `default_provider` must also appear in `configured_providers`.
- OpenAI and Anthropic require an API key before they can be marked configured.
- MCP requires a `server_url` before it can be marked configured.

### `GET /provider/health`

Response:

```json
{
  "providers": [
    {
      "provider": "ollama",
      "status": "unavailable",
      "available": false,
      "message": "Local Ollama path not yet wired.",
      "failure": {
        "code": "not_implemented",
        "detail": "Ollama health checks are not implemented in the scaffold."
      }
    }
  ]
}
```

Rules:

- Health checks must return actionable failure reasons.
- Successful checks return `status: "ready"`, `available: true`, and no failure object.
- Unavailable checks return `status: "unavailable"`, `available: false`, and structured failure details.
- MCP must support the same core health and generation operations as other providers.

### `GET /github/connect`

Response shape:

```json
{
  "status": "stub",
  "message": "GitHub OAuth flow is not implemented in this scaffold."
}
```

Rules:

- This endpoint represents targeted import enablement only.
- The MVP does not include repository synchronization or pull request flows.

### `GET /github/repos`

Response:

```json
{
  "repos": [
    {
      "id": "demo-repo",
      "name": "demo-repo",
      "owner": "placeholder"
    }
  ]
}
```

### `GET /github/repo/{repo_id}/tree`

Path parameters:

- `repo_id` (required)

Response:

```json
{
  "repo_id": "demo-repo",
  "tree": [
    {
      "path": "src/example.py",
      "type": "blob"
    }
  ]
}
```

Rules:

- MVP browsing only needs enough metadata to let the user choose one file.

### `POST /github/import-file`

Request:

```json
{
  "repo_id": "demo-repo",
  "path": "src/example.py",
  "ref": "HEAD"
}
```

Response:

```json
{
  "repo_id": "demo-repo",
  "path": "src/example.py",
  "content": "def example():\n    pass\n",
  "status": "imported"
}
```

Rules:

- MVP only supports importing a single Python file into the same path used by upload and paste.
- Imported content must be treated like any other submitted `CodeAsset`.

## Error Handling

Common error cases:

- `400`: invalid input, unsupported file type, syntax issues, or malformed config
- `404`: missing submission, candidate, exercise, or repository path
- `502`: provider failure or schema-parse failure from provider output

Errors should be explicit enough for the user to correct the issue without exposing secrets, raw prompts, or full code bodies.
