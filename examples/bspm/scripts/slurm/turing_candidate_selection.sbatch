#!/usr/bin/env bash
#SBATCH --job-name=bspm_candidates
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=12:00:00
#SBATCH --output=logs/slurm/%x_%j.out
#SBATCH --error=logs/slurm/%x_%j.err

set -euo pipefail

# Required at submit time when Turing paths differ from local paths:
#   RAW_PATH=/path/to/892_BSPM/superfile
#   NODE_LABEL_PATH=/path/to/node_label.xlsx
#
# Example:
#   sbatch --export=ALL,RAW_PATH="/data/.../superfile",NODE_LABEL_PATH="/data/.../node_label.xlsx" examples/bspm/scripts/slurm/turing_candidate_selection.sbatch

CONFIG="${CONFIG:-examples/bspm/configs/bspm_baseline.yaml}"
RUN_ID="${RUN_ID:-turing_forward_greedy_v1}"
K_VALUES="${K_VALUES:-3 6 8 12 16 24 32 48 64}"
METHODS="${METHODS:-forward_greedy}"
WORKERS="${WORKERS:-${SLURM_CPUS_PER_TASK:-16}}"
CONDA_BIN="${CONDA_BIN:-/home/gyoon/miniconda3/bin/conda}"

if [[ -z "${RAW_PATH:-}" ]]; then
  echo "RAW_PATH is required. Set it to Turing's Superfile directory." >&2
  exit 2
fi

if [[ -z "${NODE_LABEL_PATH:-}" ]]; then
  echo "NODE_LABEL_PATH is required. Set it to Turing's node_label.xlsx path." >&2
  exit 2
fi

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

mkdir -p logs/slurm

echo "pwd=$PWD"
echo "config=$CONFIG"
echo "run_id=$RUN_ID"
echo "raw_path=$RAW_PATH"
echo "node_label_path=$NODE_LABEL_PATH"
echo "k_values=$K_VALUES"
echo "methods=$METHODS"
echo "workers=$WORKERS"
echo "slurm_job_id=${SLURM_JOB_ID:-local}"
echo "slurm_cpus_per_task=${SLURM_CPUS_PER_TASK:-unset}"

"$CONDA_BIN" run -n torchgpu python examples/bspm/scripts/bspm.py select-candidates \
  --config "$CONFIG" \
  --raw-path "$RAW_PATH" \
  --node-label-path "$NODE_LABEL_PATH" \
  --run-id "$RUN_ID" \
  --k $K_VALUES \
  --methods $METHODS \
  --workers "$WORKERS"
