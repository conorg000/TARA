#!/bin/bash
# Screen A ROUND 3 — the own-stake / discovered-conflict family (plan appendix A3;
# see make_screen_a.py ROUND3_LEVERS for literature ancestry + validity tags).
# 12 evals: 6 levers x (action + pressured ask). Reuses the round-1 clean-ask and
# L0 baseline (same seed-777 docs). Same config as rounds 1-2.
set -e
cd "$(dirname "$0")"
MODEL=openrouter/qwen/qwen3-32b

for lever in G1_goal_conflict G2_self_preservation G3_moral_conflict G4_task_failure G5_collusive_precedent G6_discovered_countermand; do
    MAXTOK=512 ./.venv/bin/inspect eval inspect_gate.py@watchlist_action \
        --model $MODEL -T dataset_path=inputs/screen_a_${lever}_action.json --epochs 1
    MAXTOK=256 ./.venv/bin/inspect eval inspect_gate.py@watchlist_recognise \
        --model $MODEL -T dataset_path=inputs/screen_a_${lever}_ask.json --epochs 1
done
echo "Screen A round 3 runs complete."
