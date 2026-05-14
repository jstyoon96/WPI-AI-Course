# Turing Slurm Runbook

This workflow assumes the user logs in to Turing manually. Do not store SSH
passwords in this repository.

## 1. Get the Code From GitHub

After logging in to Turing:

```bash
cd <TURING_PROJECT_PARENT>
git clone https://github.com/jstyoon96/dl_research_template.git dl_research_template
cd dl_research_template
git switch codex/bspm-candidate-selection
```

If the repository already exists:

```bash
cd <TURING_REPO_PATH>
git fetch origin
git switch codex/bspm-candidate-selection
git pull --ff-only
```

## 2. Check Environment and Data Paths

The fixed Turing scripts use:

```bash
REPO_PATH="/home/gyoon/projects/dl_research_template"
DATA_ROOT="/home/gyoon/scratch/datasets/bspm_reconstruction/Dal_BSPM"
```

They first try:

```bash
RAW_PATH="$DATA_ROOT/Dal_BSPM/892_BSPM/superfile"
NODE_LABEL_PATH="$DATA_ROOT/Dal_BSPM/node_label.xlsx"
```

and fall back to:

```bash
RAW_PATH="$DATA_ROOT/892_BSPM/superfile"
NODE_LABEL_PATH="$DATA_ROOT/node_label.xlsx"
```

Preflight:

```bash
cd "$REPO_PATH"

DATA_ROOT="/home/gyoon/scratch/datasets/bspm_reconstruction/Dal_BSPM"
RAW_PATH="$DATA_ROOT/Dal_BSPM/892_BSPM/superfile"
NODE_LABEL_PATH="$DATA_ROOT/Dal_BSPM/node_label.xlsx"
if [ ! -d "$RAW_PATH" ]; then RAW_PATH="$DATA_ROOT/892_BSPM/superfile"; fi
if [ ! -f "$NODE_LABEL_PATH" ]; then NODE_LABEL_PATH="$DATA_ROOT/node_label.xlsx"; fi

test -d "$RAW_PATH"
test -f "$NODE_LABEL_PATH"
source ~/envs/torchgpu/bin/activate
python -c "import numpy, scipy, yaml; print(numpy.__version__, scipy.__version__, yaml.__version__)"
python -m pytest tests/unit tests/smoke examples/bspm/tests
```

## 3. Slurm Smoke Job

Run a small smoke first. This submits one fixed script; no long `--export`
command is needed. The smoke uses the full record set but only `k=3`, with
16 CPU workers and a 12 hour limit. It writes checkpoint/progress files after
each greedy step.

```bash
sbatch examples/bspm/scripts/slurm/turing_forward_greedy_smoke.sbatch
```

Monitor:

```bash
squeue -u "$USER"
tail -f slurm_<JOB_ID>.out
tail -f slurm_<JOB_ID>.err
```

If `examples/bspm/experiments/candidate_selection_v1/turing_greedy_smoke/` is missing, check
the Slurm log first:

```bash
sacct -j <JOB_ID> --format=JobID,State,ExitCode,Elapsed,MaxRSS
cat slurm_<JOB_ID>.out
cat slurm_<JOB_ID>.err
```

Live progress:

```bash
tail -f /scratch/gyoon/experiments/bspm_reconstruction/logs/greedy_smoke/progress_<JOB_ID>.log
tail -f examples/bspm/experiments/candidate_selection_v1/turing_greedy_smoke/forward_greedy_progress.csv
cat examples/bspm/experiments/candidate_selection_v1/turing_greedy_smoke/forward_greedy_checkpoint.json
```

## 4. Full Forward-Greedy Job

After the smoke output has all expected files:

```bash
sbatch examples/bspm/scripts/slurm/turing_forward_greedy_full.sbatch
```

The full script uses `--resume` and `--max-runtime-minutes 690`, so it exits
cleanly before the 12 hour Slurm limit and can be submitted again with the same
run id to continue from `forward_greedy_checkpoint.json`.

If Turing requires a different partition or account, edit the `#SBATCH` header
in the script or add flags at submission time.

## 5. Expected Outputs

Raw outputs:

```text
examples/bspm/experiments/candidate_selection_v1/<RUN_ID>/
```

Tracked summary:

```text
examples/bspm/reports/candidate_selection_v1/<RUN_ID>_summary.md
```

Expected files:

- `summary.csv`
- `selected_nodes.csv`
- `per_node_metrics.csv`
- `segment_metrics.csv`
- `forward_greedy_checkpoint.json`
- `forward_greedy_progress.csv`
- `run_manifest.json`
- `report.md`

Keep `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS`, and
`NUMEXPR_NUM_THREADS` at 1 when using multiple workers. The sbatch script sets
these values automatically.
