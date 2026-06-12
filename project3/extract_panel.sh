#!/bin/bash
# Move 2 (separability) — the PANEL GPU extraction runbook (one A100-80GB session).
#
# PRECONDITIONS (all CPU-side, all must be green before renting the box):
#   1. inputs/panel_*.json exist             (make_panel.py — done)
#   2. extract_panel_selftest.py passes      (span/group/label checks — done)
#   3. run_panel_validate.sh + observe_panel_validate.py came back all-PASS
#      (OpenRouter construction check; any failing both-cell item reauthored/dropped
#       and make_panel.py re-run)                                   <-- NOT YET RUN
#   4. git committed (clean SHA stamped into the npz meta — commit before running!)
#
# Box setup per LOGISTICS.md (git clone the public TARA repo). Then from project3/:
#   bash extract_panel.sh
# Smoke first (tiny model, 4 docs, CPU-safe), then the 7 real passes. ~212 docs/pass,
# 7 prefill positions fp16 (+ gen-prefix on the action pass) — comparable to the Exp 2
# session (~1GB/pass on disk; a few hours total).
# Pull home: acts/panel_*__*.npz  (or at minimum run probe_panel.py on-box and pull
# probe_panel.json — the flaky-uplink lesson from thread-1).
set -e
cd "$(dirname "$0")"
MODEL="${MODEL:-Qwen/Qwen3-32B}"
ACTS=acts
mkdir -p $ACTS logs

echo "== smoke (tiny model, 4 docs) =="
python extract_panel.py --model Qwen/Qwen3-0.6B --device cpu --dtype float32 \
    --dataset inputs/panel_ask_legal_p1.json --out-prefix /tmp/panel_extract_smoke --max-examples 4

echo "== ask passes (6) =="
for cond in legal medical; do
    for k in 1 2 3; do
        python extract_panel.py --model "$MODEL" \
            --dataset inputs/panel_ask_${cond}_p${k}.json \
            --out-prefix $ACTS/panel_ask_${cond}_p${k} 2>&1 | tee logs/extract_panel_ask_${cond}_p${k}.log
    done
done

echo "== action pass (1, multi-rule; includes gen-prefix) =="
python extract_panel.py --model "$MODEL" \
    --dataset inputs/panel_action.json \
    --out-prefix $ACTS/panel_action 2>&1 | tee logs/extract_panel_action.log

echo "== done. Now (laptop or on-box): python probe_panel.py --acts-dir $ACTS --out probe_panel.json =="
