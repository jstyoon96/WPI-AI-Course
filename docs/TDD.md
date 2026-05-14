# TDD

## Required Tests
1. config validation test
2. dataset loading test
3. batch shape test
4. model forward test
5. finite loss test
6. one-step backward test
7. tiny overfit test
8. fast-dev-run train test
9. evaluation smoke test
10. report generation test
11. forbidden-file modification test

## Initial Skeleton Tests
- `tests/unit/test_config.py` validates that `configs/base.yaml` exists and contains required top-level keys.
- `tests/smoke/test_smoke_imports.py` validates that the `harness` package and initial subpackages are importable.

## Required Commands
```bash
pytest tests/unit
python3 scripts/train.py --config configs/base.yaml --dry-run
python3 scripts/train.py --config configs/base.yaml --fast-dev-run
python3 scripts/evaluate.py --config configs/base.yaml --run-id smoke_test --small
python3 scripts/generate_report.py --latest
```

If a command fails, report the failure and likely cause.
