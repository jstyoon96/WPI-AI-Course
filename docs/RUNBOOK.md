# RUNBOOK

## Setup
Use the existing `torchgpu` conda environment for this workspace. Do not create
a project-local `.venv` for normal development unless the environment strategy
changes.

Use `conda run -n torchgpu` for commands that may need CUDA. Use the environment
Python executable directly for pytest because `conda run` can interfere with
pytest capture.

```bash
/home/gyoon/miniconda3/bin/conda run -n torchgpu python --version
/home/gyoon/miniconda3/bin/conda run -n torchgpu python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

## Run Tests
```bash
/home/gyoon/miniconda3/envs/torchgpu/bin/python -m pytest tests/unit tests/smoke
```

## Run Dry Train
```bash
/home/gyoon/miniconda3/bin/conda run -n torchgpu python scripts/train.py --config configs/base.yaml --dry-run
```

## Run Smoke Train
```bash
/home/gyoon/miniconda3/bin/conda run -n torchgpu python scripts/train.py --config configs/base.yaml --fast-dev-run
```

## Run Small Evaluation
```bash
/home/gyoon/miniconda3/bin/conda run -n torchgpu python scripts/evaluate.py --config configs/base.yaml --run-id smoke_test --small
```

## Generate Report
```bash
/home/gyoon/miniconda3/bin/conda run -n torchgpu python scripts/generate_report.py --latest
```

## Add A Project
1. Fill in `docs/DATA_SPEC.md` and `docs/METRIC_SPEC.md`.
2. Add project adapters in a project package or under `examples/<project>/`.
3. Add a project config based on `configs/base.yaml`.
4. Add unit tests for data loading, shape contracts, metrics, and smoke paths.
5. Keep generated run outputs under ignored `experiments/` directories.

## Worked Examples
Example-specific commands are documented beside each example. For the BSPM
worked example, see `examples/bspm/docs/` and run:

```bash
/home/gyoon/miniconda3/envs/torchgpu/bin/python -m pytest examples/bspm/tests
```

## Submit Slurm Job
Prepare the command or script, then request explicit approval before
submission. Do not call `sbatch` directly without approval.

```bash
/home/gyoon/miniconda3/bin/conda run -n torchgpu python scripts/submit_slurm.py --config experiments/EXP_ID/config.yaml --stage proxy
```

## Monitor Slurm Job
```bash
/home/gyoon/miniconda3/bin/conda run -n torchgpu python scripts/monitor_slurm.py --job-id JOB_ID
```

## Sync Results
```bash
/home/gyoon/miniconda3/bin/conda run -n torchgpu python scripts/sync_results.py --run-id EXP_ID
```

## Recover From Failed Job
1. Preserve logs and config.
2. Classify the failure.
3. Do not change metrics, labels, or split rules silently.
4. Create or update the next experiment proposal.
