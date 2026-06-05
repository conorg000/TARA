#!/usr/bin/env bash
# One-shot pipeline: smoke test -> full extraction -> probe training.
#
# Usage:
#   ./run.sh                                          # GPU defaults: Qwen3-8B, cuda, bf16, conditions_v1
#   ./run.sh Qwen/Qwen3-0.6B cpu float32              # Mac dry-run on conditions_v1
#   ./run.sh Qwen/Qwen3-0.6B cpu float32 inputs/conditions_v2.json   # ...on the semantic v2
#   ./run.sh <model> <device> <dtype> <dataset> <tag> # general form
#
# Output .npz is named after the dataset (+ optional <tag>), so runs don't clobber
# each other: activations_conditions_v2.npz, activations_conditions_v2_8b_think.npz...
# A <tag> is needed when two runs share a dataset (e.g. thinking on vs off on v2).
#
# THINK=1 enables Qwen3 thinking-mode (auto 1024-token generation budget). Off by
# default. The 8B scale x reasoning runs pre-registered in runlog.md (r7/r8):
#   ./run.sh Qwen/Qwen3-8B cuda bfloat16 inputs/conditions_v2.json 8b_nothink         # r7
#   THINK=1 ./run.sh Qwen/Qwen3-8B cuda bfloat16 inputs/conditions_v2.json 8b_think   # r8
#
# The Mac dry-run uses a deliberately weak model. On v1 its AUROC is meaningless
# (the task is too easy). On v2 it's the actual test: the theory says a tiny model
# should *struggle* on the semantic task — if it still maxes out, that's a red flag
# to investigate, not a win.

set -euo pipefail

MODEL="${1:-Qwen/Qwen3-8B}"
DEVICE="${2:-cuda}"
DTYPE="${3:-bfloat16}"
DATASET="${4:-inputs/conditions_v1.json}"
TAG="${5:-}"
OUT="activations_$(basename "$DATASET" .json)${TAG:+_$TAG}.npz"

THINK_FLAG=""
if [[ "${THINK:-0}" == "1" ]]; then
    THINK_FLAG="--enable-thinking"
fi

# Tee everything to a UTC-timestamped logfile so results survive a dropped SSH or
# frozen terminal. UTC (not the box's local clock) so the name means the same
# instant on any machine it's later read or copied to.
mkdir -p logs
RUN_TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="logs/$(basename "$DATASET" .json)${TAG:+_$TAG}_${RUN_TS}.log"
exec > >(tee -a "$LOG") 2>&1

echo "=================================================================="
echo " model=$MODEL  device=$DEVICE  dtype=$DTYPE  thinking=${THINK:-0}"
echo " dataset=$DATASET  ->  $OUT"
echo " log=$LOG  (UTC)  host=$(hostname)"
echo "=================================================================="

echo
echo ">>> [1/3] Smoke test (4 examples) — verifies model load + template + generate + save"
python extract_activations.py --model "$MODEL" --device "$DEVICE" --dtype "$DTYPE" \
    --dataset "$DATASET" --generate $THINK_FLAG --max-examples 4 --out smoke.npz

echo
echo ">>> [2/3] Full extraction + generation (all examples)"
python extract_activations.py --model "$MODEL" --device "$DEVICE" --dtype "$DTYPE" \
    --dataset "$DATASET" --generate $THINK_FLAG --out "$OUT"

echo
echo ">>> [3/3] Train probes (CPU) — AUROC per layer + verdict"
python train_probe.py --activations "$OUT"

echo
echo "Done. If you saw a verdict line above, the pipeline works end to end."
