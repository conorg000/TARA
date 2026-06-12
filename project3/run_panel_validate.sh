#!/bin/bash
# Move 2 (separability) — PANEL construction validation (OpenRouter coarse, ask-only).
# DO NOT treat these numbers as findings: coarse shapes, greedy-on-GPU scores.
#
# Asks all 212 panel docs under both conditions' questions, 3 paraphrases each, INSIDE
# the multi-rule prompt (6 evals). What this checks, before any GPU spend:
#   - capability survives the multi-rule context (own hits YES >= 90%);
#   - the NEW both-cell reads YES under BOTH questions (its existence check);
#   - behavioural cross-specificity (other-condition hits NO) and K2 (nears NO) hold
#     in the panel context;
#   - the loaded-ask phrasing ("do not produce the triage record") actually yields
#     [YES]/[NO] answers rather than triage records (UNCLEAR rate is the tell).
# Then: ./.venv/bin/python observe_panel_validate.py
# Any both-cell item that fails both-YES is reauthored or dropped BEFORE the keeper
# extraction (screens choose, keepers measure).
set -e
cd "$(dirname "$0")"
MODEL=openrouter/qwen/qwen3-32b

for cond in legal medical; do
    for k in 1 2 3; do
        MAXTOK=256 ./.venv/bin/inspect eval inspect_gate.py@screening_ask \
            --model $MODEL -T dataset_path=inputs/panel_ask_${cond}_p${k}.json --epochs 1
    done
done
echo "Panel construction validation complete. Now: ./.venv/bin/python observe_panel_validate.py"
