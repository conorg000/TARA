#!/bin/bash
# Screen B — OpenRouter coarse pass (research_plan_2026-06-11.md, Stage 0).
# 12 evals on openrouter/qwen/qwen3-32b, no-think, T=0:
#   4 candidates x 3 question paraphrases, 48 items each (ask-only — no action pass).
# Gate B (consistency >=90% core, near-miss false-fire <=10%, swap partner) is scored
# on greedy GPU numbers for the FINALIST; this pass picks the finalist.
# Then: ./.venv/bin/python observe_screen_b.py
set -e
cd "$(dirname "$0")"
MODEL=openrouter/qwen/qwen3-32b

for cand in legal_advice medical_advice override_attempt cancel_intent; do
    for k in 1 2 3; do
        MAXTOK=256 ./.venv/bin/inspect eval inspect_gate.py@screening_ask \
            --model $MODEL -T dataset_path=inputs/screen_b_${cand}_p${k}.json --epochs 1
    done
done
echo "Screen B runs complete."
