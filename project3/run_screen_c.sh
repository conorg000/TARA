#!/bin/bash
# Screen C — load titration, OpenRouter coarse pass (Experiment 1c, plan appendix A4).
# 8 evals on openrouter/qwen/qwen3-32b, no-think, T=0 (the probe-matched regime):
#   base clean-ask (160) + D0/D1 actions (80 each) + D1 ask (80)
#   + D2/D3 batch actions (26 triples each, bigger MAXTOK: 3 docs per completion)
#   + D2/D3 per-position asks (78 each).
# MAXTOK: singles 512 (runlog convention), batches 1280 (truncation fakes omissions),
# asks 256. Then: ./.venv/bin/python observe_screen_c.py
set -e
cd "$(dirname "$0")"
MODEL=openrouter/qwen/qwen3-32b

MAXTOK=256 ./.venv/bin/inspect eval inspect_gate.py@watchlist_recognise \
    --model $MODEL -T dataset_path=inputs/screen_c_base.json --epochs 1

for dose in D0 D1; do
    MAXTOK=512 ./.venv/bin/inspect eval inspect_gate.py@watchlist_action \
        --model $MODEL -T dataset_path=inputs/screen_c_${dose}_action.json --epochs 1
done
MAXTOK=256 ./.venv/bin/inspect eval inspect_gate.py@watchlist_recognise \
    --model $MODEL -T dataset_path=inputs/screen_c_D1_ask.json --epochs 1

for dose in D2 D3; do
    MAXTOK=1280 ./.venv/bin/inspect eval inspect_gate.py@watchlist_action \
        --model $MODEL -T dataset_path=inputs/screen_c_${dose}_action.json --epochs 1
    MAXTOK=256 ./.venv/bin/inspect eval inspect_gate.py@watchlist_recognise \
        --model $MODEL -T dataset_path=inputs/screen_c_${dose}_ask.json --epochs 1
done
echo "Screen C runs complete."
