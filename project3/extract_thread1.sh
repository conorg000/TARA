#!/usr/bin/env bash
# THREAD-1 GPU EXTRACTION — recognition under instructed suppression (1b) + the clean
# attention-gap contrast arm (1c: D1 brevity, D4 length). One box session.
#
# Pre-registration: research_plan_2026-06-11.md A2 (1b) + A4 Resolution (D1/D4 arm).
# SELF-CONTAINED from a fresh `git clone` — re-extracts the v6 ask recognition axis on
# the box (the banked acts/v6_ask__*.npz are gitignored and will NOT be present). This
# SUPERSEDES extract_l6.sh (which assumed a pre-existing acts/v6_ask).
#
# Box: one 80GB card (A100-80GB / H100), Qwen3-32B bf16 (~64GB). Fresh env:
#   pip install torch transformers accelerate numpy scikit-learn
#   export HF_HOME=<disk with ~65GB>   # model download is the slow part; do it first
#
# Order: smoke -> PILOT GATE (A2 spend gate; STOPS the run if it fails) -> v6 ask axis
#        -> 1b (L6) -> D1 (brevity) -> D4 (length). ~9 passes, ~1.5h after model load.
# Commit before running so the stamped SHA isn't -dirty (CLAUDE.md).
#
# Usage (on the box, from project3/):  ./extract_thread1.sh
set -euo pipefail
export PYTHONUNBUFFERED=1

MODEL="${1:-Qwen/Qwen3-32B}"
DEVICE="${2:-cuda}"
DTYPE="${3:-bfloat16}"
PY="${PYTHON:-python}"

mkdir -p acts logs
TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="logs/extract_thread1_${TS}.log"
exec > >(tee -a "$LOG") 2>&1

ex() {  # ex <dataset> <out-prefix> [extra extractor args...]
  local ds="$1" out="$2"; shift 2
  echo; echo ">>> extract  $ds  ->  $out"
  $PY extract_keyphrase.py --model "$MODEL" --device "$DEVICE" --dtype "$DTYPE" \
      --dataset "inputs/$ds" --out-prefix "$out" "$@"
}

echo "=================================================================="
echo " THREAD-1 EXTRACT  model=$MODEL  dtype=$DTYPE  log=$LOG"
echo "=================================================================="

# 1. Smoke (4 items) — verify load + no-think template + span-finding + recognition sane.
#    GATE: present (ids end 'a') should print beh=YES, absent ('b') beh=NO. Else STOP.
ex watchlist_v6_ask.json /tmp/smoke_thread1 --max-examples 4
echo ">>> smoke done — confirm beh=YES on 'a' ids, beh=NO on 'b' ids before continuing."

# 2. PILOT GATE (A2): L6 action, first 40 pairs (80 items). Stops the run if greedy
#    compliance < 6/40 (set -e on the non-zero exit). This is the pre-registered spend gate.
ex watchlist_v6_l6_action_H5.json acts/l6pilot_action --max-examples 80
echo; echo ">>> A2 pilot gate:"
$PY l6_pilot_check.py acts/l6pilot_action__final.npz   # exit 1 => set -e aborts here

# 3. Recognition axis (shared by 1b AND D1 — both are the v6 docs): full v6 ask pass.
#    This replaces the gitignored banked acts/v6_ask so the box is self-contained.
ex watchlist_v6_ask.json acts/v6_ask

# 4. 1b — instructed suppression (L6 countermand on the v6 docs).
ex watchlist_v6_l6_action_H5.json   acts/v6l6_action
ex watchlist_v6_l6_plainask_H5.json acts/v6l6_plainask

# 5. D1 — brevity attention gap (doc-matched to 1b; reuses the v6 ask axis above).
ex watchlist_v6_d1_action_H5.json   acts/v6d1_action
ex watchlist_v6_d1_plainask_H5.json acts/v6d1_plainask

# 6. D4 — length attention gap (own long docs => its OWN ask axis).
ex watchlist_d4long_ask.json        acts/d4long_ask
ex watchlist_d4long_action_H5.json  acts/d4long_action
ex watchlist_d4long_plainask_H5.json acts/d4long_plainask

echo
echo "=================================================================="
echo " DONE. Per-pass behaviour summaries are above — scan for:"
echo "   * any 'WARNING: N/.. generations hit the .. cap' on ACTION passes"
echo "     (a truncated NOFLAG fakes a gap) -> re-run that pass with --max-new-tokens 768"
echo "   * ask passes: present-YES near ceiling, absent-NO near ceiling"
echo " Pull home (small-ish; npz are bf16 activations):"
echo "   scp -r <box>:.../project3/acts/{v6_ask,v6l6_*,v6d1_*,d4long_*}__*.npz acts/"
echo " Then CPU analysis here (no GPU)."
echo "=================================================================="
