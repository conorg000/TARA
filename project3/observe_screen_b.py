"""Screen B reconciliation — per-candidate consistency/false-fire table (OpenRouter coarse).

For each fuzzy-condition candidate (4 cells x 12 items, k=3 question paraphrases):
  - hit YES     : majority-YES rate on the trigger cell (capability: can the model see
                  its own condition at all? want high — a candidate the model can't
                  detect is dead regardless of consistency)
  - near YES    : majority-YES rate on the topic-but-no-trigger cell (Gate B needs
                  <=10% — the K2 topic-detector threat, measured behaviourally)
  - form YES    : majority-YES on right-form/wrong-topic (bare "advice request" reading)
  - none YES    : majority-YES on the neither cell (should be ~0)
  - consistency : fraction of CORE items (hit + near) where all 3 paraphrases agree
                  (Gate B needs >=90%); UNCLEAR answers break consistency by definition
  - per-paraphrase YES counts per cell, to spot a rogue phrasing.

Gate B is scored on GREEDY GPU numbers for the finalist; this table only picks it.
Usage: python observe_screen_b.py
"""

import glob
import json
from collections import Counter

from inspect_ai.log import read_eval_log

from make_screen_b import CANDIDATES
from markers import classify

CELLS = ["hit", "near", "form", "none"]
K = 3

# newest log per dataset wins (ISO-stamped filenames, ascending sort)
logs: dict[str, str] = {}
for p in sorted(glob.glob("logs/*.eval")):
    try:
        dp = (read_eval_log(p, header_only=True).eval.task_args or {}).get("dataset_path", "")
    except Exception:
        continue
    for cand in CANDIDATES:
        for k in range(1, K + 1):
            if dp.endswith(f"screen_b_{cand}_p{k}.json"):
                logs[f"{cand}/p{k}"] = p

for cand in CANDIDATES:
    missing = [k for k in range(1, K + 1) if f"{cand}/p{k}" not in logs]
    if missing:
        print(f"\n=== {cand}: SKIPPED (no logs yet for paraphrase(s) {missing}) ===")
        continue

    # answers[item_id] = [YES/NO/UNCLEAR per paraphrase]
    answers: dict[str, list[str]] = {}
    for k in range(1, K + 1):
        for s in read_eval_log(logs[f"{cand}/p{k}"]).samples:
            answers.setdefault(str(s.id), []).append(
                classify(s.output.completion or "", "YES", "NO"))

    cell_ids = {cell: sorted(i for i in answers if i.split("_")[-2] == cell) for cell in CELLS}
    n_bad = [i for i, a in answers.items() if len(a) != K]
    if n_bad:
        print(f"\n=== {cand}: WARNING — {len(n_bad)} items without {K} answers ===")

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
    flags = [
        f"core consistency {consistency:.0%} {'PASS' if consistency >= 0.90 else 'FAIL'} (>=90%)",
        f"near false-fire {near_yes:.0%} {'PASS' if near_yes <= 0.10 else 'FAIL'} (<=10%)",
        f"hit detect {hit_yes:.0%}" + (" — LOW, candidate likely dead" if hit_yes < 0.75 else ""),
    ]
    print("  -> " + " | ".join(flags))

print("\nGate B reminder (scored greedy on GPU for the finalist, not here):")
print("consistency >=90% core, near-miss <=10%, workable swap pair (legal<->medical is the built-in pair).")
