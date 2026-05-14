---
name: "ml-research-harness"
description: "Use when working in this repository on the general ML research harness: configs, registries, scripts, audits, reports, diagnostics, planners, hooks, or experiment policy."
---

# ML Research Harness

## Required Reading
Before editing harness code or configs, read the relevant docs:

- `AGENTS.md`
- `docs/PRD.md`
- `docs/TRD.md`
- `docs/TDD.md`
- `docs/EDD.md`
- `docs/METRIC_SPEC.md`
- `docs/FAILURE_TAXONOMY.md`
- `docs/EXPERIMENT_POLICY.md`

## Safety Rules
- Do not change dataset splits, metric definitions, label generation rules, or final report selection criteria unless the user explicitly asks for that change.
- Do not run full training, Slurm submission, multi-GPU jobs, or large sweeps without explicit approval.
- Do not print, store, or commit secrets, SSH private keys, passwords, API keys, tokens, or full environment dumps.
- Prefer minimal patches and keep domain-specific logic out of the generic harness skeleton.

## Default Workflow
1. Inspect the current docs/configs/scripts first.
2. State the smallest implementation plan needed for the task.
3. Implement one coherent change.
4. Run safe checks: unit/smoke tests, dry-run, fast-dev-run, small eval, report generation.
5. Report changed files, tests, results, risks, and next recommended step.

## Useful Commands
Use the project `torchgpu` environment in this workspace:

```bash
/home/gyoon/miniconda3/bin/conda run -n torchgpu python scripts/train.py --config configs/base.yaml --dry-run
/home/gyoon/miniconda3/bin/conda run -n torchgpu python scripts/train.py --config configs/base.yaml --fast-dev-run
/home/gyoon/miniconda3/bin/conda run -n torchgpu python scripts/evaluate.py --config configs/base.yaml --run-id smoke_test --small
/home/gyoon/miniconda3/bin/conda run -n torchgpu python scripts/generate_report.py --latest
```
