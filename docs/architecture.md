# Architecture

## Summary

Refactor Trainer uses a monolithic architecture with a FastAPI backend and a React + TypeScript frontend.

This scaffold establishes the major seams needed for future implementation:

- `ModelProvider` abstraction for local, remote, and MCP-backed model providers
- `GuidanceRetriever` abstraction for repo-local guidance now, with a clean seam for future Strata-backed retrieval
- route-level API skeletons for ingestion, candidate handling, exercises, hints, provider setup, and GitHub import placeholders

## Backend

The backend is organized by responsibility:

- `api/`: FastAPI routes only
- `services/`: orchestration and placeholder business flows
- `providers/`: provider interface and stub implementations
- `guidance/`: guidance retriever interface and local implementation
- `schemas/`: request and response models
- `storage/`: local in-memory placeholder persistence
- `config/`: settings models

## Frontend

The frontend is intentionally minimal:

- page-level views for the requested workflow stages
- a Monaco-based editor placeholder
- lightweight API client and provider loading hook

## Deferred By Design

- real provider SDK execution
- repository-wide analysis
- non-local inference orchestration
- Strata coupling
- GitHub auth and import implementation beyond route scaffolding

