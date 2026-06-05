#!/usr/bin/env bash
# THE GPU STEP — extract activations (and behaviour) only. No probe training.
#
# This is the single thing that needs a GPU: run the model over each example and
# dump the residual-stream activations to an .npz. All probing happens afterwards
# on the laptop, off the saved .npz (see LOGISTICS.md). Pull the .npz home, then
# you can destroy the box.
#
# Usage:
#   ./extract.sh <model> <device> <dtype> <dataset> <tag>
#
#   # r8 — 8B, thinking on, with behaviour:
#   THINK=1 ./extract.sh Qwen/Qwen3-8B cuda bfloat16 inputs/conditions_v2.json 8b_think
#   # r9 — 8B transfer target (thinking off); we still generate (capture more than we need):
#   ./extract.sh Qwen/Qwen3-8B cuda bfloat16 inputs/conditions_v2b.json 8b_nothink
#
# Toggles (env vars):
#   THINK=1     Qwen3 thinking mode (auto 1024-token budget when generating). Default off.
#   GENERATE=0  skip behaviour generation. Default ON — we lean toward capturing more than
#               a given test strictly needs, because re-getting it means re-renting a GPU.
#
# Output: activations_<dataset>[_<tag>].npz  +  logs/extract_<...>_<UTC>.log

set -euo pipefail
export PYTHONUNBUFFERED=1          # stream per-example progress live (don't buffer to file)

MODEL="${1:-Qwen/Qwen3-8B}"
DEVICE="${2:-cuda}"
DTYPE="${3:-bfloat16}"
DATASET="${4:-inputs/conditions_v2.json}"
TAG="${5:-}"
OUT="activations_$(basename "$DATASET" .json)${TAG:+_$TAG}.npz"

THINK_FLAG=""; [[ "${THINK:-0}" == "1" ]] && THINK_FLAG="--enable-thinking"
GEN_FLAG="--generate"; [[ "${GENERATE:-1}" == "0" ]] && GEN_FLAG=""

mkdir -p logs
RUN_TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="logs/extract_$(basename "$DATASET" .json)${TAG:+_$TAG}_${RUN_TS}.log"
exec > >(tee -a "$LOG") 2>&1        # everything also to a UTC-named logfile (survives SSH death)

echo "=================================================================="
echo " EXTRACT (GPU)  model=$MODEL  device=$DEVICE  dtype=$DTYPE"
echo "   thinking=${THINK:-0}  generate=${GENERATE:-1}"
echo " dataset=$DATASET  ->  $OUT"
echo " log=$LOG  (UTC)  host=$(hostname)"
echo "=================================================================="

echo
echo ">>> [1/2] smoke (4 examples) — verify load + chat template + generate + save"
python extract_activations.py --model "$MODEL" --device "$DEVICE" --dtype "$DTYPE" \
    --dataset "$DATASET" $GEN_FLAG $THINK_FLAG --max-examples 4 --out smoke.npz

echo
echo ">>> [2/2] full extraction (all examples)"
python extract_activations.py --model "$MODEL" --device "$DEVICE" --dtype "$DTYPE" \
    --dataset "$DATASET" $GEN_FLAG $THINK_FLAG --out "$OUT"

echo
echo "Done. Now pull it home and probe locally (see LOGISTICS.md):"
echo "    scp arena:/root/TARA/project3/$OUT ."
echo "    python train_probe.py --activations $OUT"
