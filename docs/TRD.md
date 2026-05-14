# TRD

## Architecture
The harness is config-driven and separates data preparation, model construction, training, evaluation, diagnostics, planning, and reporting.

## Module Boundaries
- `harness.data`: dataset adapters, split loading, and audit helpers.
- `harness.models`: model adapters and prediction interfaces.
- `harness.losses`: loss registry and loss builders.
- `harness.trainers`: training loops and stage policies.
- `harness.evaluators`: metric computation and evaluation outputs.
- `harness.diagnostics`: failure classification and evidence collection.
- `harness.planners`: next-experiment proposal generation.
- `harness.runners`: local and HPC execution helpers.
- `harness.reports`: human-readable and machine-readable reports.
- `harness.registry`: shared registries.

## Recommended Interfaces
```python
class DataAdapter:
    def prepare(self, cfg): ...
    def train_loader(self): ...
    def val_loader(self): ...
    def test_loader(self): ...

class ModelAdapter:
    def build(self, cfg): ...
    def forward(self, batch): ...
    def compute_loss(self, batch, outputs): ...
    def predict(self, batch): ...

class Evaluator:
    def evaluate(self, model, dataloader, cfg): ...
    def save_metrics(self, output_dir): ...

class FailureDiagnoser:
    def diagnose(self, metrics, audit_reports, history): ...

class ExperimentPlanner:
    def propose_next(self, failure_report, experiment_history): ...
```

## Runners
- Local runner: supports dry runs, fast-dev-runs, smoke evaluations, and report generation.
- Slurm/HPC runner: prepares scripts and validates configs; submission requires explicit approval.

## Reporting
Every completed experiment must write machine-readable metrics and human-readable summaries under `experiments/EXP_ID/`.

