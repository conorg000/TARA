#!/bin/bash
# Screen A THINKING SWEEP (plan appendix A5) — THINK=1 rerun of ALL 17 levers + clean-ask.
# DIAGNOSTIC ONLY, never gate-eligible (the probe regime is no-think): tests whether the
# 17-lever null was "won't defect" or "can't defect without a reasoning scratchpad", and
# harvests CoT — an omission whose CoT names the term/watchlist is an overt
# notice-don't-act record.
#
# Logs go to logs_think/ so the no-think gate record in logs/ is never shadowed
# (observers pick newest-per-dataset). Generous MAXTOK: the <think> block spends budget
# before the answer, and truncation fakes omissions.
# Then:
#   ./.venv/bin/python observe_screen_a.py --log-dir logs_think
#   ./.venv/bin/python screen_a_transcripts.py --log-dir logs_think --out screen_a_omissions_think.md
set -e
cd "$(dirname "$0")"
MODEL=openrouter/qwen/qwen3-32b
LOGDIR=logs_think

THINK=1 MAXTOK=2048 ./.venv/bin/inspect eval inspect_gate.py@watchlist_recognise \
    --model $MODEL --log-dir $LOGDIR -T dataset_path=inputs/screen_a_ask.json --epochs 1

for lever in L0_none L1_throughput L2_plea L3_authority L4_confidentiality L5_self_interest L6_countermand \
             R1_system_scrutiny R2_authorisation_gate R3_combined_social R4_crisis R5_precedent \
             G1_goal_conflict G2_self_preservation G3_moral_conflict G4_task_failure G5_collusive_precedent G6_discovered_countermand; do
    THINK=1 MAXTOK=4096 ./.venv/bin/inspect eval inspect_gate.py@watchlist_action \
        --model $MODEL --log-dir $LOGDIR -T dataset_path=inputs/screen_a_${lever}_action.json --epochs 1
    if [ "$lever" != "L0_none" ]; then
        THINK=1 MAXTOK=2048 ./.venv/bin/inspect eval inspect_gate.py@watchlist_recognise \
            --model $MODEL --log-dir $LOGDIR -T dataset_path=inputs/screen_a_${lever}_ask.json --epochs 1
    fi
done
echo "Screen A thinking sweep complete."
