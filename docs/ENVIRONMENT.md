# ENVIRONMENT

## Project Python Environment

Use the existing conda environment:

```text
/home/gyoon/miniconda3/envs/torchgpu
```

Run CUDA or torch commands through `conda run` so conda activation sets the
right library paths:

```bash
/home/gyoon/miniconda3/bin/conda run -n torchgpu python ...
```

Run pytest through the environment Python executable directly:

```bash
/home/gyoon/miniconda3/envs/torchgpu/bin/python -m pytest ...
```

Do not create a project-local `.venv` for normal development unless the
template's environment strategy changes.

## Verified Environment

Last checked in this workspace:

```text
python: /home/gyoon/miniconda3/envs/torchgpu/bin/python
torch: 2.11.0+cu128
cuda_available: True
numpy: available
sklearn: available
pandas: available
pytest: available
```

## Development Dependency Policy

- Keep runtime dependencies minimal until a concrete pipeline needs them.
- `pytest` is installed so unit tests can run inside `torchgpu`.
- Any new external package should be documented here and justified by the
  pipeline step that needs it.

## Standard Commands

```bash
/home/gyoon/miniconda3/envs/torchgpu/bin/python -m pytest tests/unit tests/smoke
/home/gyoon/miniconda3/bin/conda run -n torchgpu python scripts/train.py --config configs/base.yaml --dry-run
/home/gyoon/miniconda3/bin/conda run -n torchgpu python scripts/evaluate.py --config configs/base.yaml --run-id smoke_test --small
```

Worked examples may document extra dependencies and commands under
`examples/<project>/docs/`.
