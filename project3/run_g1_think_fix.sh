#!/bin/bash
# G1-only THINK=1 rerun with a generous token cap (runlog A5 follow-up). The original
# sweep truncated 16/40 G1 action samples at MAXTOK=4096 — goal-conflict induced ~20k-char
# reasoning that blew the cap, so empty answers were lost (not omissions, just cut off).
# Here MAXTOK is large enough that the think block finishes; logs land in logs_think/ and
# supersede the truncated G1 logs (observers pick newest-per-dataset).
#
# Worth doing for more than tidiness: a full-reasoning G1 sample could show a genuinely
# goal-MOTIVATED omission ("a FLAG gets the batch rejected → defeats my objective → omit"),
# which is the one interesting motivated case the truncation currently hides.
#
# After: ./.venv/bin/python observe_screen_a.py --log-dir logs_think
#        ./.venv/bin/python screen_a_transcripts.py --log-dir logs_think --out screen_a_omissions_think.md
set -e
cd "$(dirname "$0")"
MODEL=openrouter/qwen/qwen3-32b
LOGDIR=logs_think

THINK=1 MAXTOK=16384 ./.venv/bin/inspect eval inspect_gate.py@watchlist_action \
    --model $MODEL --log-dir $LOGDIR -T dataset_path=inputs/screen_a_G1_goal_conflict_action.json --epochs 1

THINK=1 MAXTOK=8192 ./.venv/bin/inspect eval inspect_gate.py@watchlist_recognise \
    --model $MODEL --log-dir $LOGDIR -T dataset_path=inputs/screen_a_G1_goal_conflict_ask.json --epochs 1

echo "G1 think-fix complete. Re-run the two observers (--log-dir logs_think)."
