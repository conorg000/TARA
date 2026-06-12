#!/bin/bash
# Move 3 / Step 4 — keeper construction validation, OpenRouter coarse pass.
# Runs the panel loaded-ask passes (multi-rule context — exactly what the GPU will label
# on) so the keeper content is de-risked BEFORE the GPU session. screening_ask, qwen3-32b,
# no-think, T=0: N survivors x 3 paraphrases, 248 docs each.
# Then: ./.venv/bin/python observe_playbook_validate.py
set -e
cd "$(dirname "$0")"
MODEL=openrouter/qwen/qwen3-32b

CONDS="${1:-data_deletion fraud_report implicit_legal_threat}"

for cond in $CONDS; do
    for k in 1 2 3; do
        MAXTOK=256 ./.venv/bin/inspect eval inspect_gate.py@screening_ask \
            --model $MODEL -T dataset_path=inputs/playbook_ask_${cond}_p${k}.json --epochs 1
    done
done
echo "Playbook construction-validation runs complete."
