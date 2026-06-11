#!/bin/bash
# Experiment 2 keeper extraction — run on the GPU box once 1b/1c frees it.
# 8 passes (6 ask + 2 action) × 184 docs on Qwen3-32B, no-think, greedy/T=0 (deterministic),
# generous message-relative positions (extract_exp2.py). Writes acts/exp2_*__<position>.npz
# in the keyphrase schema, so the probe code consumes them unchanged.
#
# Span-finding + CV grouping are pre-verified off-GPU by extract_exp2_selftest.py
# (char + group + token-level via the real tokenizer — all pass). The smoke pass below
# re-confirms on the actual 32B before the full run.
#
# Commit before running so the activations are stamped with a clean SHA (extract_exp2.py
# records git_commit per the repo convention).
set -e
cd "$(dirname "$0")"
PY=${PY:-./.venv-gpu/bin/python}      # the box's GPU venv (same as the 1b/1c run)
MODEL=${MODEL:-Qwen/Qwen3-32B}
mkdir -p acts

echo ">>> smoke (4 items, real model — verifies span-finding + behaviour on-box)"
$PY extract_exp2.py --model "$MODEL" --dataset inputs/exp2_keeper_ask_legal_p1.json \
    --out-prefix /tmp/exp2_smoke --max-examples 4

for cond in legal medical; do
  for k in 1 2 3; do
    echo ">>> ask $cond p$k"
    $PY extract_exp2.py --model "$MODEL" \
        --dataset inputs/exp2_keeper_ask_${cond}_p${k}.json \
        --out-prefix acts/exp2_ask_${cond}_p${k}
  done
  echo ">>> action $cond"
  $PY extract_exp2.py --model "$MODEL" \
      --dataset inputs/exp2_keeper_action_${cond}.json \
      --out-prefix acts/exp2_action_${cond}
done
echo "Exp 2 extraction complete: acts/exp2_*__<position>.npz"
