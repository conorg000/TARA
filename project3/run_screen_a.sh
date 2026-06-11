#!/bin/bash
# Screen A — OpenRouter coarse pass (research_plan_2026-06-11.md, Stage 0).
# 14 evals on openrouter/qwen/qwen3-32b, no-think, T=0:
#   1 clean-ask (80 items) + 7 lever actions (40 each) + 6 pressured asks (40 each).
# MAXTOK: 512 for H5 action (runlog convention — truncation fakes omissions), 256 for asks.
# Then: ./.venv/bin/python observe_screen_a.py
set -e
cd "$(dirname "$0")"
MODEL=openrouter/qwen/qwen3-32b

MAXTOK=256 ./.venv/bin/inspect eval inspect_gate.py@watchlist_recognise \
    --model $MODEL -T dataset_path=inputs/screen_a_ask.json --epochs 1

for lever in L0_none L1_throughput L2_plea L3_authority L4_confidentiality L5_self_interest L6_countermand; do
    MAXTOK=512 ./.venv/bin/inspect eval inspect_gate.py@watchlist_action \
        --model $MODEL -T dataset_path=inputs/screen_a_${lever}_action.json --epochs 1
    if [ "$lever" != "L0_none" ]; then
        MAXTOK=256 ./.venv/bin/inspect eval inspect_gate.py@watchlist_recognise \
            --model $MODEL -T dataset_path=inputs/screen_a_${lever}_ask.json --epochs 1
    fi
done
echo "Screen A runs complete."
