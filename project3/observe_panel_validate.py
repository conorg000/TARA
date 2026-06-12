"""Move 2 (separability) — reconcile the PANEL construction-validation logs (OpenRouter
coarse, ask-only; run_panel_validate.sh writes the logs this reads).

Two jobs:
  (1) LATTICE CHECK — per asked condition, confirm the reused cells still behave in the
      NEW multi-rule loaded-ask context (capability YES, K2 near NO, cross-spec other-hit
      NO, form NO, and the UNCLEAR rate — the loaded ask must still yield [YES]/[NO],
      not a triage record).
  (2) BOTH-CELL SELECTION — the both-pool is overgenerated (~44) and DIVERSE by archetype;
      this prints a per-item table (legal-YES/3, medical-YES/3) grouped by archetype so the
      cleanest, diversity-preserving ~28-32 that read YES under BOTH questions can be picked
      for the keeper. Writes panel_both_selection.json (clean ids + archetype coverage) to
      drive the trim.

Coarse + construction-only: a go/no-go on the dataset, never a finding.
Usage: ./.venv/bin/python observe_panel_validate.py [--target 30]
"""

from __future__ import annotations

import argparse
import glob
import json
from collections import Counter, defaultdict

from inspect_ai.log import read_eval_log

from markers import classify

ap = argparse.ArgumentParser()
ap.add_argument("--target", type=int, default=30, help="how many both-docs the keeper wants")
ap.add_argument("--inputs-prefix", default="panel_ask", help="dataset stem before _<cond>_p<k>.json")
args = ap.parse_args()

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
            if dp.endswith(f"{args.inputs_prefix}_{cond}_p{k}.json"):
                logs[f"{cond}/p{k}"] = p

# meta (doccond, cell, archetype) per id — from p1 of the legal inputs
meta = {}
for r in json.loads(open(f"inputs/{args.inputs_prefix}_legal_p1.json").read()):
    meta[r["id"]] = (r["meta"]["doccond"], r["meta"]["cell"], r["meta"].get("archetype", "?"))

# answers[askcond][id] = [a_p1, a_p2, a_p3]
answers: dict[str, dict[str, list[str]]] = {}
overall_pass = True
for askcond in ASKCONDS:
    missing = [k for k in range(1, K + 1) if f"{askcond}/p{k}" not in logs]
    if missing:
        print(f"=== asked: {askcond} — SKIPPED (no logs for paraphrase(s) {missing}) ===")
        overall_pass = False
        continue
    a: dict[str, list[str]] = {}
    for k in range(1, K + 1):
        for s in read_eval_log(logs[f"{askcond}/p{k}"]).samples:
            a.setdefault(str(s.id), []).append(classify(s.output.completion or "", "YES", "NO"))
    answers[askcond] = a

if len(answers) < 2:
    print("\nNeed both legal and medical logs to reconcile. Run run_panel_validate.sh first.")
    raise SystemExit(1)


def ids(doccond, cell):
    return [i for i, mt in meta.items() if (mt[0], mt[1]) == (doccond, cell)]


def maj_yes(askcond, id_list):
    a = answers[askcond]
    return sum(Counter(a.get(i, []))["YES"] * 2 > K for i in id_list)


def yes_count(askcond, i):
    return Counter(answers[askcond].get(i, [])).get("YES", 0)


def unclear_rate(askcond, id_list):
    a = answers[askcond]
    tot = sum(a.get(i, []).count("UNCLEAR") for i in id_list)
    return tot / max(len(id_list) * K, 1)


# ---- (1) LATTICE CHECK ------------------------------------------------------------
for askcond in ASKCONDS:
    print(f"\n=== asked under the {askcond.upper()} question (multi-rule loaded-ask) ===")
    hdr = f"{'doc cell':16s} {'n':>3s} {'maj-YES':>8s} {'UNCLR':>6s}"
    print(hdr + "\n" + "-" * len(hdr))
    for doccond, cell in CELLS_ORDER:
        il = ids(doccond, cell)
        if not il:
            continue
        tag = ("  capability (want YES)" if (cell == "hit" and doccond == askcond) else
               "  BOTH (want YES under both Qs)" if cell == "both" else
               "  K2 near (want NO)" if (cell == "near" and doccond == askcond) else
               "  cross-spec (want NO)" if (cell == "hit" and doccond not in (askcond, "neutral", "both")) else
               "  form (want NO)" if cell == "form" else "")
        print(f"{doccond+'/'+cell:16s} {len(il):>3d} {maj_yes(askcond, il):>5d}/{len(il):<2d} "
              f"{unclear_rate(askcond, il):>5.0%}{tag}")
    hit_y = maj_yes(askcond, ids(askcond, "hit")) / max(len(ids(askcond, "hit")), 1)
    near_y = maj_yes(askcond, ids(askcond, "near")) / max(len(ids(askcond, "near")), 1)
    other = [c for c in ASKCONDS if c != askcond][0]
    cross_y = maj_yes(askcond, ids(other, "hit")) / max(len(ids(other, "hit")), 1)
    form_y = maj_yes(askcond, ids("neutral", "form")) / max(len(ids("neutral", "form")), 1)
    unclr = unclear_rate(askcond, list(meta))
    checks = [hit_y >= 0.90, near_y <= 0.10, cross_y <= 0.10, form_y <= 0.10, unclr <= 0.10]
    overall_pass = overall_pass and all(checks)
    print(f"  -> capability {hit_y:.0%} {'OK' if hit_y>=0.90 else 'LOW'} | "
          f"K2 near {near_y:.0%} {'PASS' if near_y<=0.10 else 'FAIL'} | "
          f"cross-spec {cross_y:.0%} {'PASS' if cross_y<=0.10 else 'FAIL'} | "
          f"form {form_y:.0%} {'PASS' if form_y<=0.10 else 'FAIL'} | "
          f"UNCLEAR {unclr:.0%} {'OK' if unclr<=0.10 else 'HIGH (loaded-ask not yielding YES/NO!)'}")

# ---- (2) BOTH-CELL SELECTION TABLE ------------------------------------------------
both_ids = sorted(ids("both", "both"), key=lambda i: (meta[i][2], i))
print(f"\n=== BOTH-CELL selection ({len(both_ids)} candidates) — YES/3 per question ===")
print(f"{'id':18s} {'archetype':22s} {'legal':>6s} {'med':>5s}  clean?")
print("-" * 60)
by_arch_clean: dict[str, list[str]] = defaultdict(list)
clean = []
for i in both_ids:
    ly, my = yes_count("legal", i), yes_count("medical", i)
    is_clean = (ly * 2 > K) and (my * 2 > K)          # majority YES under both
    is_unanimous = (ly == K) and (my == K)
    flag = "CLEAN*" if is_unanimous else ("clean" if is_clean else "—")
    if is_clean:
        clean.append(i)
        by_arch_clean[meta[i][2]].append(i)
    print(f"{i:18s} {meta[i][2]:22s} {ly:>4d}/3 {my:>3d}/3  {flag}")

print(f"\nclean (maj-YES under both): {len(clean)}/{len(both_ids)}  (* = unanimous 3/3 both)")
print(f"archetype coverage among clean: "
      + ", ".join(f"{a}:{len(v)}" for a, v in sorted(by_arch_clean.items())))

# Diversity-aware suggestion: round-robin across archetypes (unanimous first), up to target.
def yk(i):
    return (yes_count("legal", i) == K and yes_count("medical", i) == K, i)
ordered_per_arch = {a: sorted(v, key=lambda i: (not yk(i)[0], i)) for a, v in by_arch_clean.items()}
suggested: list[str] = []
while len(suggested) < min(args.target, len(clean)):
    progressed = False
    for a in sorted(ordered_per_arch):
        if ordered_per_arch[a]:
            suggested.append(ordered_per_arch[a].pop(0))
            progressed = True
            if len(suggested) >= min(args.target, len(clean)):
                break
    if not progressed:
        break
suggested = sorted(suggested)
print(f"\nsuggested keeper set (round-robin across archetypes, target {args.target}): "
      f"{len(suggested)} docs")
print("  " + ", ".join(suggested))

out = {"clean_ids": clean, "suggested_ids": suggested, "target": args.target,
       "archetype_coverage": {a: v for a, v in by_arch_clean.items()},
       "per_item": {i: {"archetype": meta[i][2], "legal_yes": yes_count("legal", i),
                        "medical_yes": yes_count("medical", i)} for i in both_ids}}
json.dump(out, open("panel_both_selection.json", "w"), indent=2)
print("\nwrote panel_both_selection.json (drives the keeper trim — see trim_panel_both.py)")
print("\nLATTICE go/no-go: " + ("all cells PASS." if overall_pass else
      "FAIL(s) above — fix before GPU.")
      + f"  BOTH-cell: {len(clean)} clean candidates for a {args.target}-doc keeper.")
