# API Spec

This document describes the scaffold-level API contract.

## Routes

### `GET /health`

Returns application health and scaffold status.

### `POST /submit-code`

Accepts a code submission payload and returns a placeholder submission record.

### `GET /candidates`

Returns deterministic placeholder candidates for a submission.

### `POST /exercise/{candidate_id}`

Returns a placeholder exercise generated for a candidate.

### `GET /hints/{exercise_id}`

Returns placeholder hints for an exercise.

### `POST /submit-attempt/{exercise_id}`

Returns placeholder attempt feedback.

### `GET /providers`

Lists configured provider stubs.

### `GET /provider/config`

Returns current placeholder provider configuration.

### `PUT /provider/config`

Updates placeholder provider configuration in local memory.

### `GET /provider/health`

Runs provider health checks via the provider abstraction.

### `GET /github/connect`

Placeholder entry point for future GitHub connection flow.

### `GET /github/repos`

Returns placeholder repositories.

### `GET /github/repo/{repo_id}/tree`

Returns a placeholder repository tree.

### `POST /github/import-file`

Returns placeholder imported file metadata.

