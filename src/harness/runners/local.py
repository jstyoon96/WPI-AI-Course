"""Local runner placeholders for safe harness checks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RunnerResult:
    stage: str
    status: str
    message: str


def dry_run(config_path: str | Path) -> RunnerResult:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(path)
    return RunnerResult(stage="dry-run", status="passed", message=f"Config exists: {path}")


def fast_dev_run(config_path: str | Path) -> RunnerResult:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(path)
    return RunnerResult(stage="fast-dev-run", status="passed", message=f"Smoke path exists: {path}")

