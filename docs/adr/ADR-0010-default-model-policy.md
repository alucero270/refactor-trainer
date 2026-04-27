# ADR-0010: Default Provider Model Policy

## Status

Accepted.

## Context

Each remote provider (OpenAI, Anthropic) has a `default_model` that is used when
the user configures the provider without specifying a model. These defaults must
track the current production-capable model for each vendor so that a fresh
install is usable without manual tuning.

Historically the defaults drifted: `claude-sonnet-4-20250514` was shipped for
months after Anthropic's Sonnet family had advanced to 4.5 and 4.6, and
`gpt-5` was left in place without an explicit policy for when to revise it.

## Decision

The `default_model` constant on each provider class in `backend/app/providers/`
is the single source of truth for what a fresh install uses.

The defaults are revised whenever:

1. The vendor releases a new generation of their general-purpose model (new
   major or minor family, not patch versions).
2. The vendor deprecates or retires the current default.
3. A release cycle for this project touches provider code for any other reason.

Any change to `default_model` requires:

- updating the provider's unit tests to reference the new default (if they pin it)
- noting the change in the PR description
- verifying the new model is reachable via each provider's health check

User-configured models (via `/provider/config`) always override the default
and are not affected by this policy.

## Consequences

- Defaults stay roughly current without a background job or external config.
- Breaking model renames surface as health-check failures on fresh installs,
  which is surfaced in the Provider Setup UI — acceptable, since the user can
  override via config.
- Does not introduce runtime model discovery; defaults remain static constants.
