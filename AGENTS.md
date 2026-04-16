# AGENTS.md

## Repo Layout

- `backend/`: FastAPI application scaffold, provider abstractions, guidance seam, tests
- `frontend/`: React + TypeScript application scaffold with Monaco editor placeholder
- `docs/`: architecture notes, API spec, ADRs, prompts, repo-local guidance content
- `.github/workflows/`: CI baseline

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

## Test Commands

```bash
cd backend
pytest
```

```bash
cd frontend
npm run build
```

## Scaffold Constraints

- Keep the architecture monolithic.
- Prefer placeholder implementations over speculative product logic.
- Preserve clean seams for providers, guidance retrieval, and future MCP-backed extensions.
- Treat Ollama as the reference local-first provider path, while keeping OpenAI, Anthropic, and MCP as BYOK placeholders.

## Do-Not-Overbuild Rules

- Do not implement full GitHub OAuth or repository synchronization.
- Do not implement real provider SDK calls in this pass.
- Do not implement real MCP transport in this pass.
- Do not build cross-file or repository-wide analysis.
- Do not add hosted/shared inference, collaboration, gamification, accounts, or social features.
- Do not tightly couple guidance retrieval to Strata yet.
- Do not turn placeholder tests into fabricated deep-logic tests.

