#!/bin/bash
#SBATCH -N 1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64g
#SBATCH -J bspm_greedy_full
#SBATCH -o /home/gyoon/projects/dl_research_template/slurm_%j.out
#SBATCH -e /home/gyoon/projects/dl_research_template/slurm_%j.err
#SBATCH -p short
#SBATCH -t 0-12:00:00

set -e
set -o pipefail
set -x

source ~/envs/torchgpu/bin/activate

cd /home/gyoon/projects/dl_research_template

LOG_DIR="/scratch/gyoon/experiments/bspm_reconstruction/logs/greedy_full"
JOB_ID="${SLURM_JOB_ID:-local}"
mkdir -p "$LOG_DIR"
cp "slurm_${JOB_ID}.out" "$LOG_DIR/slurm_${JOB_ID}.out.start" 2>/dev/null || true
trap 'cp "slurm_${JOB_ID}.out" "$LOG_DIR/slurm_${JOB_ID}.out" 2>/dev/null || true; cp "slurm_${JOB_ID}.err" "$LOG_DIR/slurm_${JOB_ID}.err" 2>/dev/null || true' EXIT

export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

DATA_ROOT="/home/gyoon/scratch/datasets/bspm_reconstruction/Dal_BSPM"
RAW_PATH="$DATA_ROOT/Dal_BSPM/892_BSPM/superfile"
NODE_LABEL_PATH="$DATA_ROOT/Dal_BSPM/node_label.xlsx"

if [ ! -d "$RAW_PATH" ]; then
  RAW_PATH="$DATA_ROOT/892_BSPM/superfile"
fi

if [ ! -f "$NODE_LABEL_PATH" ]; then
  NODE_LABEL_PATH="$DATA_ROOT/node_label.xlsx"
fi

test -d "$RAW_PATH"
test -f "$NODE_LABEL_PATH"

python -u examples/bspm/scripts/bspm.py select-candidates \
  --config examples/bspm/configs/bspm_baseline.yaml \
  --raw-path "$RAW_PATH" \
  --node-label-path "$NODE_LABEL_PATH" \
  --run-id turing_forward_greedy_v1 \
  --k 3 6 8 12 16 24 32 48 64 \
  --methods forward_greedy \
  --workers 16 \
  --resume \
  --max-runtime-minutes 690 \
  2>&1 | tee -a "$LOG_DIR/progress_${JOB_ID}.log"
