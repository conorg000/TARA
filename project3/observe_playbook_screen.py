"""Move 3 / Step 3 — pre-test reconciliation: per-condition Gate B table (OpenRouter coarse).

Mirrors observe_screen_b.py. For each condition (4 cells x 12 items, k=3 paraphrases):
  hit YES     : majority-YES on the trigger cell (capability — want >=75%)
  near YES    : majority-YES on the topic-but-no-trigger cell (Gate B needs <=10%; K2 threat)
  form/none   : bare-form reading / baseline
  consistency : fraction of CORE items (hit+near) where all 3 paraphrases agree (>=90%)

Gate B (PLAYBOOK Step 3): consistency >=90% core, near false-fire <=10%, hit detect >=75%.
A miss here KILLS the condition (counts in the yield denominator). No redesign in cold mode.

Usage: ./.venv/bin/python observe_playbook_screen.py
"""

import glob
import json
from collections import Counter
from pathlib import Path

from inspect_ai.log import read_eval_log

from markers import classify

CELLS = ["hit", "near", "form", "none"]
K = 3

CONDS = list(json.loads((Path(__file__).parent / "playbook_screen_content.json").read_text()).keys())

# newest log per dataset wins (ISO-stamped filenames, ascending sort)
logs: dict[str, str] = {}
for p in sorted(glob.glob("logs/*.eval")):
    try:
        dp = (read_eval_log(p, header_only=True).eval.task_args or {}).get("dataset_path", "")
    except Exception:
        continue
    for cand in CONDS:
        for k in range(1, K + 1):
            if dp.endswith(f"playbook_screen_{cand}_p{k}.json"):
                logs[f"{cand}/p{k}"] = p

summary = {}
for cand in CONDS:
    missing = [k for k in range(1, K + 1) if f"{cand}/p{k}" not in logs]
    if missing:
        print(f"\n=== {cand}: SKIPPED (no logs yet for paraphrase(s) {missing}) ===")
        continue

    answers: dict[str, list[str]] = {}
    for k in range(1, K + 1):
        for s in read_eval_log(logs[f"{cand}/p{k}"]).samples:
            answers.setdefault(str(s.id), []).append(
                classify(s.output.completion or "", "YES", "NO"))

    cell_ids = {cell: sorted(i for i in answers if i.split("_")[-2] == cell) for cell in CELLS}

    def majority_yes(ids: list[str]) -> int:
        return sum(Counter(answers[i])["YES"] * 2 > K for i in ids)

    def unanimous(ids: list[str]) -> int:
        return sum(len(set(answers[i])) == 1 and answers[i][0] != "UNCLEAR" for i in ids)

    print(f"\n=== {cand} ===")
    hdr = f"{'cell':6s} {'n':>3s} {'maj-YES':>8s} {'unanim':>7s} {'UNCLEAR':>8s}  per-paraphrase YES"
    print(hdr + "\n" + "-" * len(hdr))
    for cell in CELLS:
        ids = cell_ids[cell]
        per_k = [sum(answers[i][k] == "YES" for i in ids) for k in range(K)]
        unclear = sum(a == "UNCLEAR" for i in ids for a in answers[i])
        print(f"{cell:6s} {len(ids):>3d} {majority_yes(ids):>5d}/{len(ids):<2d} "
              f"{unanimous(ids):>4d}/{len(ids):<2d} {unclear:>8d}  {per_k}")

    core = cell_ids["hit"] + cell_ids["near"]
    consistency = unanimous(core) / len(core) if core else 0.0
    hit_yes = majority_yes(cell_ids["hit"]) / max(len(cell_ids["hit"]), 1)
    near_yes = majority_yes(cell_ids["near"]) / max(len(cell_ids["near"]), 1)
    cons_pass = consistency >= 0.90
    near_pass = near_yes <= 0.10
    hit_pass = hit_yes >= 0.75
    gate = cons_pass and near_pass and hit_pass
    flags = [
        f"core consistency {consistency:.0%} {'PASS' if cons_pass else 'FAIL'} (>=90%)",
        f"near false-fire {near_yes:.0%} {'PASS' if near_pass else 'FAIL'} (<=10%)",
        f"hit detect {hit_yes:.0%} {'PASS' if hit_pass else 'FAIL'} (>=75%)",
    ]
    print("  -> " + " | ".join(flags))
    print(f"  -> GATE B: {'PASS — proceed to keeper' if gate else 'FAIL — killed at pre-test'}")
    summary[cand] = {"consistency": round(consistency, 3), "near_fire": round(near_yes, 3),
                     "hit_detect": round(hit_yes, 3), "gate_b_pass": gate}

if summary:
    Path("playbook_screen_summary.json").write_text(json.dumps(summary, indent=2))
    passed = [c for c, v in summary.items() if v["gate_b_pass"]]
    print(f"\nWrote playbook_screen_summary.json. Gate B survivors ({len(passed)}/{len(summary)} observed): "
          + (", ".join(passed) if passed else "none"))
