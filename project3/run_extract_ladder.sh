#!/bin/bash
# Move 4 (spontaneity ladder) extraction — run on the GPU box (A100-80GB, Qwen3-32B).
# 4 candidates x (3 ask_compound + 2 ask_comp + 2 read) = 28 passes x 80 docs, no-think,
# greedy/T=0. ask -> [YES]/[NO] (training labels); read -> FLAG/noFLAG (pure-reading arms).
# Writes acts/ladder_*__<position>.npz in the keyphrase schema (probe consumes unchanged).
#
# Span-finding + grouping pre-verified off-GPU by extract_ladder_selftest.py (char + group +
# token-level, all pass). The smoke pass re-confirms on the real 32B before the full run.
# Commit before running so activations carry a clean SHA (extract_ladder.py records git_commit).
set -e
cd "$(dirname "$0")"
PY=${PY:-./.venv-gpu/bin/python}      # on the box: PY=/venv/main/bin/python
MODEL=${MODEL:-Qwen/Qwen3-32B}
mkdir -p acts

CANDS="advice_deadline refund_over_500 complaint_6months medical_rx_drug"

echo ">>> smoke (4 items, real model — verifies span-finding + behaviour on-box)"
$PY extract_ladder.py --model "$MODEL" \
    --dataset inputs/ladder_refund_over_500_ask_compound_p1.json \
    --out-prefix /tmp/ladder_smoke --max-examples 4

for cand in $CANDS; do
  for k in 1 2 3; do
    echo ">>> $cand ask_compound p$k"
    $PY extract_ladder.py --model "$MODEL" \
        --dataset inputs/ladder_${cand}_ask_compound_p${k}.json \
        --out-prefix acts/ladder_${cand}_ask_compound_p${k}
  done
  for q in compA compB; do
    echo ">>> $cand ask_$q"
    $PY extract_ladder.py --model "$MODEL" \
        --dataset inputs/ladder_${cand}_ask_${q}.json \
        --out-prefix acts/ladder_${cand}_ask_${q}
  done
  for arm in present absent; do
    echo ">>> $cand read_$arm"
    $PY extract_ladder.py --model "$MODEL" \
        --dataset inputs/ladder_${cand}_read_${arm}.json \
        --out-prefix acts/ladder_${cand}_read_${arm}
  done
done
echo "Move 4 extraction complete: acts/ladder_*__<position>.npz"
