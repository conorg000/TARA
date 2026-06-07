#!/usr/bin/env bash
# STEP 2 EXTRACTION (GPU) — dump activations + local behaviour for BOTH passes of
# conditions_v6, for the train-on-ask / test-on-action cross-pass probe.
#
# Needs an 80GB-class GPU for Qwen3-32B (bf16 ~66GB): one A100/H100 80GB, ~120GB
# disk. The 24GB 8B box will NOT hold 32B. (For 2x48GB sharding you'd need
# device_map=auto — not wired yet; ask.)
#
# Captures, per pass, for all 192 items: per-layer last-token (pre-generation)
# activations + the model's own greedy answer (so the cross-pass probe can label
# recognition from the local ask answer, and read the action cells locally rather
# than trusting the OpenRouter numbers). No-think (matches the v6 baseline).
#
# Usage (on the GPU box, from project3/):
#   ./extract_v6.sh                      # Qwen/Qwen3-32B, cuda, bfloat16, tag 32b
#   ./extract_v6.sh Qwen/Qwen3-32B cuda bfloat16 32b
#
# Then pull the two .npz home and run cross_pass_probe.py (see tail).

set -euo pipefail
export PYTHONUNBUFFERED=1

MODEL="${1:-Qwen/Qwen3-32B}"
DEVICE="${2:-cuda}"
DTYPE="${3:-bfloat16}"
TAG="${4:-32b}"

ACT_OUT="activations_conditions_v6_action_${TAG}.npz"
ASK_OUT="activations_conditions_v6_ask_${TAG}.npz"

mkdir -p logs
TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="logs/extract_v6_${TAG}_${TS}.log"
exec > >(tee -a "$LOG") 2>&1

echo "=================================================================="
echo " EXTRACT v6 (both passes)  model=$MODEL  device=$DEVICE  dtype=$DTYPE"
echo " action -> $ACT_OUT   |   ask -> $ASK_OUT"
echo " log=$LOG  (UTC)  host=$(hostname)"
echo "=================================================================="

echo
echo ">>> smoke (4 action examples) — verify 32B load + chat template + generate + save"
python extract_activations.py --model "$MODEL" --device "$DEVICE" --dtype "$DTYPE" \
    --dataset inputs/conditions_v6_action.json --generate --max-examples 4 --out smoke.npz

echo
echo ">>> ACTION pass (markers [ESCALATE]/[PROCEED])"
python extract_activations.py --model "$MODEL" --device "$DEVICE" --dtype "$DTYPE" \
    --dataset inputs/conditions_v6_action.json --generate \
    --escalate-marker "[ESCALATE]" --proceed-marker "[PROCEED]" --out "$ACT_OUT"

echo
echo ">>> ASK pass (markers [YES]/[NO])"
python extract_activations.py --model "$MODEL" --device "$DEVICE" --dtype "$DTYPE" \
    --dataset inputs/conditions_v6_ask.json --generate \
    --escalate-marker "[YES]" --proceed-marker "[NO]" --out "$ASK_OUT"

echo
echo "Done. Pull both home, then on the laptop:"
echo "    scp <box>:.../project3/activations_conditions_v6_{action,ask}_${TAG}.npz ."
echo "    ./.venv/bin/python cross_pass_probe.py --ask $ASK_OUT --action $ACT_OUT"
