#!/usr/bin/env bash
# One-shot pipeline: smoke test -> full extraction -> probe training.
#
# Usage:
#   ./run.sh                                          # GPU defaults: Qwen3-8B, cuda, bf16, conditions_v1
#   ./run.sh Qwen/Qwen3-0.6B cpu float32              # Mac dry-run on conditions_v1
#   ./run.sh Qwen/Qwen3-0.6B cpu float32 inputs/conditions_v2.json   # ...on the semantic v2
#   ./run.sh <model> <device> <dtype> <dataset>       # general form
#
# Output .npz is named after the dataset, so v1 and v2 runs don't clobber each
# other (activations_conditions_v1.npz, activations_conditions_v2.npz).
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
OUT="activations_$(basename "$DATASET" .json).npz"

echo "=================================================================="
echo " model=$MODEL  device=$DEVICE  dtype=$DTYPE"
echo " dataset=$DATASET  ->  $OUT"
echo "=================================================================="

echo
echo ">>> [1/3] Smoke test (4 examples) — verifies model load + template + generate + save"
python extract_activations.py --model "$MODEL" --device "$DEVICE" --dtype "$DTYPE" \
    --dataset "$DATASET" --generate --max-examples 4 --out smoke.npz

echo
echo ">>> [2/3] Full extraction + generation (all examples)"
python extract_activations.py --model "$MODEL" --device "$DEVICE" --dtype "$DTYPE" \
    --dataset "$DATASET" --generate --out "$OUT"

echo
echo ">>> [3/3] Train probes (CPU) — AUROC per layer + verdict"
python train_probe.py --activations "$OUT"

echo
echo "Done. If you saw a verdict line above, the pipeline works end to end."
