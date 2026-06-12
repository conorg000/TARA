#!/bin/bash
# Move 3 / Step 3 — pre-test, OpenRouter coarse pass (PLAYBOOK Step 3, Gate B).
# screening_ask on qwen3-32b, no-think, T=0: 6 conditions x 3 paraphrases, 48 items each.
# Gate B (consistency >=90% core, near false-fire <=10%, hit detect >=75%) scored by
# observe_playbook_screen.py. A miss KILLS the condition (counts in yield denominator).
set -e
cd "$(dirname "$0")"
MODEL=openrouter/qwen/qwen3-32b

CONDS="${1:-financial_advice compensation_demand data_deletion fraud_report third_party_writer implicit_legal_threat}"

for cond in $CONDS; do
    for k in 1 2 3; do
        MAXTOK=256 ./.venv/bin/inspect eval inspect_gate.py@screening_ask \
            --model $MODEL -T dataset_path=inputs/playbook_screen_${cond}_p${k}.json --epochs 1
    done
done
echo "Playbook pre-test runs complete."
