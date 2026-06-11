#!/bin/bash
# Screen A ROUND 2 — the single redesign round Gate A provides (see make_screen_a.py
# ROUND2_LEVERS rationale). 10 evals: 5 levers x (action + pressured ask). Reuses the
# round-1 clean-ask and L0 baseline (same seed-777 docs). Same config as round 1.
set -e
cd "$(dirname "$0")"
MODEL=openrouter/qwen/qwen3-32b

for lever in R1_system_scrutiny R2_authorisation_gate R3_combined_social R4_crisis R5_precedent; do
    MAXTOK=512 ./.venv/bin/inspect eval inspect_gate.py@watchlist_action \
        --model $MODEL -T dataset_path=inputs/screen_a_${lever}_action.json --epochs 1
    MAXTOK=256 ./.venv/bin/inspect eval inspect_gate.py@watchlist_recognise \
        --model $MODEL -T dataset_path=inputs/screen_a_${lever}_ask.json --epochs 1
done
echo "Screen A round 2 runs complete."
