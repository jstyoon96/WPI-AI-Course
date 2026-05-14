# ADR 0001: Initial Architecture

## Status
Accepted

## Context
The harness must support reusable ML research workflows across tasks without embedding domain-specific assumptions.

## Decision
Use a config-driven repository structure with separate modules for data, models, losses, training, evaluation, diagnostics, planning, runners, reports, and registries.

## Consequences
- Researchers can add domain adapters without changing the core harness.
- Experiment safety policies are documented separately from training code.
- Initial code contains placeholders until project-specific data and metrics are defined.

