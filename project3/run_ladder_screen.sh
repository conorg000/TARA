#!/bin/bash
# Move 4 — OpenRouter probeability screen (plan_move4 Stage 1).
# 4 candidates x (3 compound paraphrases + compA + compB) = 20 evals, ask-only,
# openrouter/qwen/qwen3-32b (matches the GPU Qwen/Qwen3-32B), no-think, T=0 greedy.
# Then: ./.venv/bin/python observe_ladder_screen.py
set -e
cd "$(dirname "$0")"
MODEL=openrouter/qwen/qwen3-32b

for cand in advice_deadline refund_over_500 complaint_6months medical_rx_drug; do
    for q in compound_p1 compound_p2 compound_p3 compA compB; do
        ./.venv/bin/inspect eval inspect_gate.py@screening_ask \
            --model $MODEL -T dataset_path=inputs/ladder_screen_${cand}_${q}.json --epochs 1
    done
done
echo "Ladder screen runs complete."
