# Refactor Trainer

Refactor Trainer is a local-first developer tool scaffold for turning real code into guided refactoring exercises.

This repository currently contains the initial monolithic architecture skeleton only:

- FastAPI backend scaffold
- React + TypeScript frontend scaffold
- Provider and guidance abstractions
- Placeholder implementations and route skeletons
- Docs, ADR, tests, Docker, and CI baseline

No deep product logic is implemented in this pass.

## Repository Layout

```text
backend/    FastAPI app, provider abstractions, tests
frontend/   React + TypeScript app scaffold
docs/       Architecture, API notes, ADRs, prompts, guidance
.github/    CI workflow
```

## Run Locally

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

## Tests

```bash
cd backend
pytest
```

## Status

Implemented now:

- scaffolded API routes
- provider contract seam
- guidance retriever seam
- placeholder docs and prompts
- CI and Docker baseline

Intentionally stubbed:

- provider SDK integration
- MCP transport details
- GitHub auth/import flow
- candidate detection heuristics beyond a deterministic stub
- exercise generation, hints, and grading logic

