#!/bin/bash
# Move 4 — re-screen the EXPANDED keeper ask files (80 docs/cell-set) on OpenRouter,
# to catch any weak new items before GPU extraction. ask passes only (YES/NO).
# Then: ./.venv/bin/python observe_ladder_keeper.py
set -e
cd "$(dirname "$0")"
MODEL=openrouter/qwen/qwen3-32b

for cand in advice_deadline refund_over_500 complaint_6months medical_rx_drug; do
    for q in ask_compound_p1 ask_compound_p2 ask_compound_p3 ask_compA ask_compB; do
        ./.venv/bin/inspect eval inspect_gate.py@screening_ask \
            --model $MODEL -T dataset_path=inputs/ladder_${cand}_${q}.json --epochs 1
    done
done
echo "Ladder keeper re-screen complete."
