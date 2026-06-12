#!/bin/bash
# Move 1 (Flow A) — regenerate the Exp 2 keeper behaviour, generation-only (no activations).
# See plan_move1_crosstab.md. The 2 action passes are REQUIRED for the cross-tab; the 6 ask
# passes are cheap and supply the consistency-filtered ask-label column. 184 docs x 8 passes,
# greedy/T=0, no-think — minutes-scale on an A100 (vs hours for a full extraction).
#
# Commit before running so the behaviour JSONs carry a clean git SHA (repo convention).
# Afterwards pull acts/crosstab_beh_*.json to the laptop and run:
#   python crosstab_exp2.py --beh-dir acts
set -e
cd "$(dirname "$0")"
PY=${PY:-./.venv-gpu/bin/python}      # the box's GPU venv (same as the exp2/1b runs)
MODEL=${MODEL:-Qwen/Qwen3-32B}
mkdir -p acts

echo ">>> smoke (4 items, real model — verifies prompt build + parsing on-box)"
$PY crosstab_behaviour_gpu.py --model "$MODEL" \
    --dataset inputs/exp2_keeper_action_legal.json \
    --out /tmp/crosstab_smoke.json --max-examples 4

for cond in legal medical; do
  echo ">>> action $cond (required)"
  $PY crosstab_behaviour_gpu.py --model "$MODEL" \
      --dataset inputs/exp2_keeper_action_${cond}.json \
      --out acts/crosstab_beh_action_${cond}.json
done
for cond in legal medical; do
  for k in 1 2 3; do
    echo ">>> ask $cond p$k (ask-label column)"
    $PY crosstab_behaviour_gpu.py --model "$MODEL" \
        --dataset inputs/exp2_keeper_ask_${cond}_p${k}.json \
        --out acts/crosstab_beh_ask_${cond}_p${k}.json
  done
done
echo "done: acts/crosstab_beh_*.json — pull to laptop, then: python crosstab_exp2.py --beh-dir acts"
