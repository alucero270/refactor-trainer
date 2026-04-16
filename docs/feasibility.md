# Feasibility

## Technical Feasibility

The MVP is feasible for a solo developer because it stays monolithic, focuses on single-file Python input, and uses deterministic analysis for most of the pipeline. Complexity rises because the product also commits to:

- a provider abstraction
- local secret handling
- MCP as a full provider path
- targeted GitHub import
- a guidance retrieval seam

Even with those additions, the plan remains workable as long as repository-wide analysis and cross-file reasoning stay out of scope.

## Product Feasibility

The product has a clear wedge: deliberate refactoring practice on real code in an AI-heavy development era. The MVP is valuable if it can reliably complete one meaningful learning loop without giving away the answer.

## Cost Posture

The MVP cost posture is favorable:

- Ollama shifts inference cost to the user's machine.
- OpenAI and Anthropic are BYOK.
- MCP cost depends on the user's configured backend.
- GitHub import adds implementation complexity but little ongoing infrastructure cost.

This makes it reasonable to validate usefulness before making SaaS pricing assumptions.

## Main Risks

- weak prompt quality
- local model inconsistency
- provider setup friction
- MCP configuration complexity
- GitHub auth and import edge cases
- users expecting repository-wide analysis instead of targeted file import

## What Is Most Likely To Break First

The earliest failure points are:

- provider setup and diagnostics
- provider output consistency and schema adherence
- GitHub import edge cases
- prompt quality that is either too vague or too revealing

## Early Validation Priorities

Validate these first:

- Ollama end-to-end usefulness
- targeted GitHub import into the normal exercise flow
- whether generated exercises and hints feel genuinely instructive
- whether the guidance pack keeps outputs aligned and non-leaky

## Pricing Fit

Do not optimize the MVP around hosted inference revenue. Validate product usefulness first. Later options can include:

- a one-time license for local-first users
- team licensing
- an optional hosted plan after MVP validation
