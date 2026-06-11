#!/usr/bin/env bash
# EXPERIMENT 1b EXTRACTION (GPU) — recognition under instructed suppression.
# Pre-registration: research_plan_2026-06-11.md appendix A2. Inputs: make_keyphrase_l6.py.
#
# Same box class as the v6 keyphrase run (80GB A100/H100 for Qwen3-32B bf16). Two
# passes over 480 items (~40% of a v6 run), with the PRE-REGISTERED PILOT GATE first:
#   smoke (4)  ->  pilot: first 40 pairs of the L6 action pass  ->  l6_pilot_check.py
#   (compliance >= 6/40, else this script STOPS)  ->  full L6 action  ->  L6 plain-ask.
#
# The ask-trained recognition direction is REUSED from the banked v6 extraction
# (acts/v6_ask__*.npz) — no new ask pass. Commit before running so the stamped SHA
# isn't -dirty (CLAUDE.md convention).
#
# Usage (on the GPU box, from project3/):  ./extract_l6.sh
set -euo pipefail
export PYTHONUNBUFFERED=1

MODEL="${1:-Qwen/Qwen3-32B}"
DEVICE="${2:-cuda}"
DTYPE="${3:-bfloat16}"

mkdir -p logs acts
TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="logs/extract_l6_${TS}.log"
exec > >(tee -a "$LOG") 2>&1

echo "=================================================================="
echo " EXTRACT 1b (L6 countermand)  model=$MODEL  dtype=$DTYPE  log=$LOG"
echo "=================================================================="

echo
echo ">>> smoke (4 items) — verify load + L6 prompt + span-location + generate + save"
python extract_keyphrase.py --model "$MODEL" --device "$DEVICE" --dtype "$DTYPE" \
    --dataset inputs/watchlist_v6_l6_action_H5.json --max-examples 4 \
    --out-prefix /tmp/smoke_l6

echo
echo ">>> PILOT: L6 action, first 40 pairs (80 items) — the A2 spend gate"
python extract_keyphrase.py --model "$MODEL" --device "$DEVICE" --dtype "$DTYPE" \
    --dataset inputs/watchlist_v6_l6_action_H5.json --max-examples 80 \
    --out-prefix acts/l6pilot_action

echo
python l6_pilot_check.py acts/l6pilot_action__final.npz
# (non-zero exit above aborts here via set -e — the pre-registered stop)

echo
echo ">>> FULL: L6 action pass (480 items)"
python extract_keyphrase.py --model "$MODEL" --device "$DEVICE" --dtype "$DTYPE" \
    --dataset inputs/watchlist_v6_l6_action_H5.json --out-prefix acts/v6l6_action

echo
echo ">>> L6 plain-ask pass (480 items — in-context recognition labels under the countermand)"
python extract_keyphrase.py --model "$MODEL" --device "$DEVICE" --dtype "$DTYPE" \
    --dataset inputs/watchlist_v6_l6_plainask_H5.json --out-prefix acts/v6l6_plainask

echo
echo "Done. Pull home:"
echo "    scp <box>:.../project3/acts/v6l6_*__*.npz acts/"
echo "Then the A2 analysis (probe_l6.py) on the laptop."
