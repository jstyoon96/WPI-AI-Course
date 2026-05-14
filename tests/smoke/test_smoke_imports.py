import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_harness_packages_import():
    modules = [
        "harness",
        "harness.data",
        "harness.models",
        "harness.losses",
        "harness.trainers",
        "harness.evaluators",
        "harness.diagnostics",
        "harness.planners",
        "harness.runners",
        "harness.runners.local",
        "harness.runners.slurm",
        "harness.reports",
        "harness.reports.contracts",
        "harness.registry",
        "harness.registry.core",
    ]

    for module in modules:
        importlib.import_module(module)


def test_registry_and_contract_smoke():
    from harness.registry import Registry
    from harness.reports import experiment_paths
    from harness.runners import dry_run, require_approval

    registry = Registry("example")
    registry.register("item", lambda: "ok")
    assert registry.names() == ["item"]
    assert registry.get("item")() == "ok"

    paths = experiment_paths("smoke_test")
    assert paths.metrics_summary.name == "metrics_summary.json"
    assert paths.failure_report.name == "failure_report.json"
    assert paths.next_experiment_proposal.name == "next_experiment_proposal.md"

    assert dry_run("configs/base.yaml").status == "passed"
    try:
        require_approval(False)
    except PermissionError:
        pass
    else:
        raise AssertionError("Slurm guard should require approval")

