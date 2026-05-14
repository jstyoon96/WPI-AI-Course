# ML Research Harness Template

Reusable scaffold for disciplined machine-learning research projects.

The harness is organized around:

```text
Data -> Audit -> Train -> Evaluate -> Diagnose -> Plan -> Patch -> Smoke Test -> Run Again -> Report
```

Use this repository as a starting point when a project needs:

- policy docs for data, metrics, failures, experiments, and runbooks
- safe placeholder CLI entrypoints for audit, train, evaluate, diagnose, plan,
  sync, and report workflows
- registries and package boundaries for data adapters, models, losses,
  trainers, evaluators, diagnostics, planners, runners, and reports
- Codex hooks, skills, and tests that enforce careful research workflow

## Instantiate A New Project

1. Copy the template.
2. Update `configs/base.yaml` with the project name and safe smoke defaults.
3. Fill in `docs/DATA_SPEC.md` and `docs/METRIC_SPEC.md` before comparing
   experiments.
4. Add project-specific adapters in your own package or under `examples/`.
5. Keep full training, Slurm submission, metric definition changes, split
   changes, and label-generation changes behind explicit human approval.

## Safe Starter Commands

```bash
/home/gyoon/miniconda3/envs/torchgpu/bin/python -m pytest tests/unit tests/smoke
/home/gyoon/miniconda3/bin/conda run -n torchgpu python scripts/train.py --config configs/base.yaml --dry-run
/home/gyoon/miniconda3/bin/conda run -n torchgpu python scripts/train.py --config configs/base.yaml --fast-dev-run
/home/gyoon/miniconda3/bin/conda run -n torchgpu python scripts/evaluate.py --config configs/base.yaml --run-id smoke_test --small
/home/gyoon/miniconda3/bin/conda run -n torchgpu python scripts/generate_report.py --latest
```

## Worked Examples

Example projects live under `examples/` and are intentionally kept outside the
generic `harness` core. The BSPM sparse-reconstruction example is in
`examples/bspm/`.

See `AGENTS.md` and `docs/` for the template policy, architecture, test plan,
metric contract, experiment policy, and runbook.
