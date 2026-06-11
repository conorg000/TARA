#!/bin/bash
# Screen C dose D4 (longer documents) — the optional registered dose (A4), run alone
# since D0-D3 already landed. 2 evals on openrouter/qwen/qwen3-32b, no-think, T=0:
#   D4 action (80 single long docs) + D4 ask (80, recognition under the long-doc load).
# Single-doc, no brevity note: isolates DOCUMENT LENGTH as the load axis.
# MAXTOK 512 action (H5 field battery, doc length doesn't grow the output) / 256 ask.
# Then: ./.venv/bin/python observe_screen_c.py
set -e
cd "$(dirname "$0")"
MODEL=openrouter/qwen/qwen3-32b

MAXTOK=512 ./.venv/bin/inspect eval inspect_gate.py@watchlist_action \
    --model $MODEL -T dataset_path=inputs/screen_c_D4_action.json --epochs 1
MAXTOK=256 ./.venv/bin/inspect eval inspect_gate.py@watchlist_recognise \
    --model $MODEL -T dataset_path=inputs/screen_c_D4_ask.json --epochs 1
echo "Screen C D4 run complete."
