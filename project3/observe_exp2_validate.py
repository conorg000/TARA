"""Experiment 2 construction-validation reconciliation (OpenRouter coarse, pre-keeper).

For each asked rule (legal, medical), over the shared 44-doc set asked under k=3
paraphrases, report per (doccond, cell): majority-YES and cross-paraphrase unanimity.
Then score the three construction tests, before any keeper is authored:

  K2 (register-matched near): under the matching question, the matching-condition NEAR
      cell must stay NO (<=10% maj-YES). If near fires, the model was reading register/
      vocabulary, not advice-seeking — the keeper's near cell needs redesign.
  K3 (behavioural rule-swap): the OTHER condition's hit cell, asked under this question,
      must read NO (the cross-rule flip). e.g. legal hits under the medical question -> NO.
  form (request-shape): the neutral advice-seeking cell must read NO under both questions.
  hit (capability): the matching-condition hit cell must read YES (>=90%).

These are coarse (OpenRouter) and on throwaway docs — a go/no-go on construction, not a
gate. Gate B itself is greedy-on-GPU on the keeper. Usage: python observe_exp2_validate.py
"""

import argparse
import glob
import json
from collections import Counter

from inspect_ai.log import read_eval_log

from markers import classify

ap = argparse.ArgumentParser()
ap.add_argument("--prefix", default="exp2_validate",
                help="dataset filename stem before _<cond>_p<k>.json (e.g. exp2_keeper_ask)")
args = ap.parse_args()
PREFIX = args.prefix

ASKCONDS = ["legal", "medical"]
K = 3
CELLS_ORDER = [("legal", "hit"), ("legal", "near"), ("medical", "hit"),
               ("medical", "near"), ("neutral", "form"), ("neutral", "none")]

# newest log per dataset wins (ISO-stamped filenames, ascending sort)
logs: dict[str, str] = {}
for p in sorted(glob.glob("logs/*.eval")):
    try:
        dp = (read_eval_log(p, header_only=True).eval.task_args or {}).get("dataset_path", "")
    except Exception:
        continue
    for cond in ASKCONDS:
        for k in range(1, K + 1):
            if dp.endswith(f"{PREFIX}_{cond}_p{k}.json"):
                logs[f"{cond}/p{k}"] = p

# meta lookup (doccond, cell) per id — same across paraphrases; read p1 of each cond
meta = {}
for cond in ASKCONDS:
    f = f"inputs/{PREFIX}_{cond}_p1.json"
    for r in json.loads(open(f).read()):
        meta[r["id"]] = (r["meta"]["doccond"], r["meta"]["cell"])

for askcond in ASKCONDS:
    missing = [k for k in range(1, K + 1) if f"{askcond}/p{k}" not in logs]
    if missing:
        print(f"\n=== asked: {askcond} — SKIPPED (no logs for paraphrase(s) {missing}) ===")
        continue

    answers: dict[str, list[str]] = {}
    for k in range(1, K + 1):
        for s in read_eval_log(logs[f"{askcond}/p{k}"]).samples:
            answers.setdefault(str(s.id), []).append(
                classify(s.output.completion or "", "YES", "NO"))

    def ids(doccond, cell):
        return [i for i in answers if meta.get(i) == (doccond, cell)]

    def maj_yes(id_list):
        return sum(Counter(answers[i])["YES"] * 2 > K for i in id_list)

    def unanim(id_list):
        return sum(len(set(answers[i])) == 1 and answers[i][0] != "UNCLEAR" for i in id_list)

    print(f"\n=== asked under the {askcond.upper()} question ===")
    hdr = f"{'doc cell':16s} {'n':>3s} {'maj-YES':>8s} {'unanim':>7s}  per-paraphrase YES"
    print(hdr + "\n" + "-" * len(hdr))
    for doccond, cell in CELLS_ORDER:
        il = ids(doccond, cell)
        if not il:
            continue
        per_k = [sum(answers[i][k] == "YES" for i in il) for k in range(K)]
        tag = "  <- capability" if (cell == "hit" and doccond == askcond) else (
              "  <- K2 register-near (want NO)" if (cell == "near" and doccond == askcond) else (
              "  <- K3 swap (want NO)" if (cell == "hit" and doccond != askcond and doccond != "neutral") else (
              "  <- form (want NO)" if cell == "form" else "")))
        print(f"{doccond+'/'+cell:16s} {len(il):>3d} {maj_yes(il):>5d}/{len(il):<2d} "
              f"{unanim(il):>4d}/{len(il):<2d}  {per_k}{tag}")

    hit_y = maj_yes(ids(askcond, "hit")) / max(len(ids(askcond, "hit")), 1)
    near_y = maj_yes(ids(askcond, "near")) / max(len(ids(askcond, "near")), 1)
    other = [c for c in ASKCONDS if c != askcond][0]
    swap_y = maj_yes(ids(other, "hit")) / max(len(ids(other, "hit")), 1)
    form_y = maj_yes(ids("neutral", "form")) / max(len(ids("neutral", "form")), 1)
    print(f"  -> hit-detect {hit_y:.0%} {'OK' if hit_y >= 0.90 else 'LOW'} | "
          f"K2 register-near {near_y:.0%} {'PASS' if near_y <= 0.10 else 'FAIL'} | "
          f"K3 swap {swap_y:.0%} {'PASS' if swap_y <= 0.10 else 'FAIL'} | "
          f"form {form_y:.0%} {'PASS' if form_y <= 0.10 else 'FAIL'}")

print("\nGo/no-go (coarse, throwaway docs): all PASS -> author the full keeper in this shape.")
print("K2 register-near FAIL -> Screen B's cleanliness was surface register; redesign the near cell before any GPU.")
