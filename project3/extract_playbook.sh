#!/bin/bash
# Move 3 / Step 5 — GPU extraction runbook (the exact commands run on the A100 box).
# Mirrors /root/run_playbook_box.sh as launched in tmux on 2026-06-12 (commit 3744649).
# Extracts all 10 playbook passes (9 ask + 1 action) of the N=3 shared multi-rule panel.
# Probing happens locally / on the box; this script only writes the .npz activations.
#
# On the box:
#   cd /root/TARA/project3 && git pull
#   tmux new-session -d -s pb "bash extract_playbook.sh > logs/playbook_extract.log 2>&1; \
#       echo PB_EXIT=\$? >> logs/playbook_extract.log"
#   # detach Ctrl-b d ; reattach: tmux attach -t pb
# Then probe on the box (sklearn is installed there):
#   /venv/main/bin/python probe_playbook.py --acts-dir acts --out probe_playbook.json
#   /venv/main/bin/python probe_playbook_lengthcontrol.py --acts-dir acts \
#       --out probe_playbook_lengthcontrol.json
# and scp the (small) *.json results home.
set -e
cd "$(dirname "$0")"
export HF_HOME=/workspace/.hf_home
export PYTHONUNBUFFERED=1
mkdir -p acts logs
PY=${PY:-/venv/main/bin/python}
MODEL=${MODEL:-Qwen/Qwen3-32B}

for cond in data_deletion fraud_report implicit_legal_threat; do
    for k in 1 2 3; do
        $PY extract_playbook.py --model "$MODEL" \
            --dataset inputs/playbook_ask_${cond}_p${k}.json \
            --out-prefix acts/playbook_ask_${cond}_p${k}
    done
done
$PY extract_playbook.py --model "$MODEL" \
    --dataset inputs/playbook_action.json --out-prefix acts/playbook_action
echo "PLAYBOOK_EXTRACT_DONE"
