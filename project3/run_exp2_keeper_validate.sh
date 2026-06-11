#!/bin/bash
# Experiment 2 keeper — SCALED construction check (coarse, ask-only). Re-runs the K2/K3
# behavioural validation on the full 184-doc keeper before any GPU: each doc asked under
# the legal and medical questions, 3 paraphrases. 6 evals on openrouter/qwen/qwen3-32b,
# no-think, T=0. Confirms register-matched near stays dark and the rule-swap flips AT
# SCALE before the expensive extraction. (Greedy ask labels + action come on the GPU box.)
# Then: ./.venv/bin/python observe_exp2_validate.py --prefix exp2_keeper_ask
set -e
cd "$(dirname "$0")"
MODEL=openrouter/qwen/qwen3-32b

for cond in legal medical; do
    for k in 1 2 3; do
        MAXTOK=256 ./.venv/bin/inspect eval inspect_gate.py@screening_ask \
            --model $MODEL -T dataset_path=inputs/exp2_keeper_ask_${cond}_p${k}.json --epochs 1
    done
done
echo "Exp 2 keeper scaled validation complete."
