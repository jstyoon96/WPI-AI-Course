# BSPM Worked Example

This example demonstrates how to instantiate the generic ML research harness for
sparse body-surface-potential reconstruction.

The example keeps all project-specific code, configs, docs, and tests outside
the generic `src/harness` package:

```text
examples/bspm/
  bspm_harness/      # example-specific parsers and evaluators
  configs/           # example config
  docs/              # example research notes and Slurm docs
  scripts/           # example command entrypoints
  tests/             # example unit tests
```

Run the example tests with:

```bash
/home/gyoon/miniconda3/envs/torchgpu/bin/python -m pytest examples/bspm/tests
```

Example candidate selection command:

```bash
/home/gyoon/miniconda3/bin/conda run -n torchgpu python examples/bspm/scripts/bspm.py select-candidates --config examples/bspm/configs/bspm_baseline.yaml --run-id smoke_candidates --max-records 3 --k 3 --methods random pca_qr forward_greedy
```

Do not submit Slurm jobs or run long experiments without explicit approval.
