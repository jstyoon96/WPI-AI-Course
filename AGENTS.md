# AGENTS.md

## Role
You are assisting with a general ML Research Harness.

The goal is to build a reusable system for:

Data -> Audit -> Train -> Evaluate -> Diagnose -> Plan -> Patch -> Smoke Test -> Run Again -> Report.

This repository is not tied to one medical, vision, language, tabular, or time-series domain.

## Required Reading Before Edits
Read the relevant files before making code changes:

- docs/PRD.md
- docs/TRD.md
- docs/TDD.md
- docs/EDD.md
- docs/DATA_SPEC.md
- docs/METRIC_SPEC.md
- docs/FAILURE_TAXONOMY.md
- docs/EXPERIMENT_POLICY.md
- docs/RUNBOOK.md

## Non-Negotiable Rules
- Do not modify the final test split unless explicitly instructed.
- Do not modify metric definitions unless explicitly instructed.
- Do not change label generation rules unless explicitly instructed.
- Do not run full training without explicit approval.
- Do not submit Slurm jobs without explicit approval.
- Do not print or store secrets, SSH keys, passwords, tokens, or API keys.
- Prefer minimal patches.
- Add or update tests for code changes.

## Required Workflow
1. Read the relevant docs.
2. Produce a concise implementation plan.
3. Identify files to change.
4. Make one minimal change.
5. Run required checks.
6. Summarize changed files, test results, risks, and next action.

## Required Checks
Run as applicable:

```bash
/home/gyoon/miniconda3/envs/torchgpu/bin/python -m pytest tests/unit
/home/gyoon/miniconda3/bin/conda run -n torchgpu python scripts/train.py --config configs/base.yaml --dry-run
/home/gyoon/miniconda3/bin/conda run -n torchgpu python scripts/train.py --config configs/base.yaml --fast-dev-run
/home/gyoon/miniconda3/bin/conda run -n torchgpu python scripts/evaluate.py --config configs/base.yaml --run-id smoke_test --small
/home/gyoon/miniconda3/bin/conda run -n torchgpu python scripts/generate_report.py --latest
```

## Forbidden Commands Without Explicit Approval
- full training commands
- sbatch submission
- destructive file deletion
- environment variable dumps
- reading SSH private keys
- git push --force

## Reporting Format
At the end of each task, report:

1. What changed
2. Why it changed
3. Files changed
4. Tests run
5. Test results
6. Risks
7. Recommended next step
