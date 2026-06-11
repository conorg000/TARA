#!/bin/bash
# Experiment 2 construction-validation — OpenRouter coarse pass (pre-keeper, throwaway).
# 6 ask-only evals on openrouter/qwen/qwen3-32b, no-think, T=0: 44 docs asked under the
# legal question and the medical question, 3 paraphrases each. Tests register-matched near
# (K2), the behavioural rule-swap (K3), and the form/request-shape control before the
# full keeper is authored. Then: ./.venv/bin/python observe_exp2_validate.py
set -e
cd "$(dirname "$0")"
MODEL=openrouter/qwen/qwen3-32b

for cond in legal medical; do
    for k in 1 2 3; do
        MAXTOK=256 ./.venv/bin/inspect eval inspect_gate.py@screening_ask \
            --model $MODEL -T dataset_path=inputs/exp2_validate_${cond}_p${k}.json --epochs 1
    done
done
echo "Exp 2 validation runs complete."
