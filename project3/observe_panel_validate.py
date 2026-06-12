"""Move 2 (separability) — reconcile the PANEL construction-validation logs (OpenRouter
coarse, ask-only; run_panel_validate.sh writes the logs this script reads).

Per asked condition (legal, medical), over the 212-doc panel lattice asked under k=3
paraphrases INSIDE the multi-rule prompt, report per (doccond, cell): majority-YES and
cross-paraphrase unanimity. Then score the construction checks:

  capability : own-condition hit cell majority-YES >= 90%.
  BOTH cell  : majority-YES >= 90% under EACH question — the new cell's existence check.
               Per-item failures are listed BY ID so they can be reauthored/dropped
               before the keeper extraction (screens choose, keepers measure).
  cross-spec : the OTHER condition's hit cell reads NO (<= 10% maj-YES) — the
               behavioural shadow of the probe kill-switch.
  K2-in-panel: own near cell stays NO (<= 10%).
  form/none  : NO (<= 10%).
  UNCLEAR    : rate per cell — the loaded-ask phrasing must still yield [YES]/[NO];
               a high UNCLEAR rate means the model produced triage records instead.

Coarse + construction-only: this is a go/no-go on the dataset, never a finding.
Usage: ./.venv/bin/python observe_panel_validate.py
"""

from __future__ import annotations

import glob
import json
from collections import Counter

from inspect_ai.log import read_eval_log

from markers import classify

ASKCONDS = ["legal", "medical"]
K = 3
CELLS_ORDER = [("legal", "hit"), ("legal", "near"), ("medical", "hit"),
               ("medical", "near"), ("both", "both"), ("neutral", "form"),
               ("neutral", "none")]

# newest log per dataset wins (ISO-stamped filenames, ascending sort)
logs: dict[str, str] = {}
for p in sorted(glob.glob("logs/*.eval")):
    try:
        dp = (read_eval_log(p, header_only=True).eval.task_args or {}).get("dataset_path", "")
    except Exception:
        continue
    for cond in ASKCONDS:
        for k in range(1, K + 1):
            if dp.endswith(f"panel_ask_{cond}_p{k}.json"):
                logs[f"{cond}/p{k}"] = p

meta = {}
for r in json.loads(open("inputs/panel_ask_legal_p1.json").read()):
    meta[r["id"]] = (r["meta"]["doccond"], r["meta"]["cell"])

both_fail_ids: dict[str, list[str]] = {}
overall_pass = True

for askcond in ASKCONDS:
    missing = [k for k in range(1, K + 1) if f"{askcond}/p{k}" not in logs]
    if missing:
        print(f"\n=== asked: {askcond} — SKIPPED (no logs for paraphrase(s) {missing}) ===")
        overall_pass = False
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

    def unclear_rate(id_list):
        tot = sum(answers[i].count("UNCLEAR") for i in id_list)
        return tot / max(len(id_list) * K, 1)

    print(f"\n=== asked under the {askcond.upper()} question (multi-rule context) ===")
    hdr = f"{'doc cell':16s} {'n':>3s} {'maj-YES':>8s} {'unanim':>7s} {'UNCLR':>6s}  per-paraphrase YES"
    print(hdr + "\n" + "-" * len(hdr))
    for doccond, cell in CELLS_ORDER:
        il = ids(doccond, cell)
        if not il:
            continue
        per_k = [sum(answers[i][k] == "YES" for i in il) for k in range(K)]
        tag = ("  <- capability (want YES)" if (cell == "hit" and doccond == askcond) else
               "  <- BOTH cell (want YES under BOTH questions)" if cell == "both" else
               "  <- K2 register-near (want NO)" if (cell == "near" and doccond == askcond) else
               "  <- cross-spec (want NO)" if (cell == "hit" and doccond not in (askcond, "neutral", "both")) else
               "  <- form (want NO)" if cell == "form" else "")
        print(f"{doccond+'/'+cell:16s} {len(il):>3d} {maj_yes(il):>5d}/{len(il):<2d} "
              f"{unanim(il):>4d}/{len(il):<2d} {unclear_rate(il):>5.0%}  {per_k}{tag}")

    hit_y = maj_yes(ids(askcond, "hit")) / max(len(ids(askcond, "hit")), 1)
    both_ids_ = ids("both", "both")
    both_y = maj_yes(both_ids_) / max(len(both_ids_), 1)
    near_y = maj_yes(ids(askcond, "near")) / max(len(ids(askcond, "near")), 1)
    other = [c for c in ASKCONDS if c != askcond][0]
    cross_y = maj_yes(ids(other, "hit")) / max(len(ids(other, "hit")), 1)
    form_y = maj_yes(ids("neutral", "form")) / max(len(ids("neutral", "form")), 1)
    both_fail_ids[askcond] = [i for i in both_ids_ if Counter(answers[i])["YES"] * 2 <= K]

    checks = [hit_y >= 0.90, both_y >= 0.90, near_y <= 0.10, cross_y <= 0.10, form_y <= 0.10]
    overall_pass = overall_pass and all(checks)
    print(f"  -> capability {hit_y:.0%} {'OK' if hit_y >= 0.90 else 'LOW'} | "
          f"BOTH {both_y:.0%} {'OK' if both_y >= 0.90 else 'LOW'} | "
          f"K2 near {near_y:.0%} {'PASS' if near_y <= 0.10 else 'FAIL'} | "
          f"cross-spec {cross_y:.0%} {'PASS' if cross_y <= 0.10 else 'FAIL'} | "
          f"form {form_y:.0%} {'PASS' if form_y <= 0.10 else 'FAIL'}")

fails = sorted(set(both_fail_ids.get("legal", [])) | set(both_fail_ids.get("medical", [])))
if fails:
    print(f"\nBOTH-cell items failing majority-YES under at least one question "
          f"({len(fails)}) — reauthor or drop BEFORE extraction:")
    for i in fails:
        print(f"  - {i}" + ("  (failed legal ask)" if i in both_fail_ids.get("legal", []) else "")
              + ("  (failed medical ask)" if i in both_fail_ids.get("medical", []) else ""))

print("\nGo/no-go (coarse, construction-only): "
      + ("all checks PASS -> proceed to extract_panel.sh on the box."
         if overall_pass else
         "FAIL(s) above -> fix the named items / cells before any GPU spend."))
