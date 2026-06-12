"""Move 4 ladder screen — per-candidate probeability gate table (OpenRouter coarse).

Reads the newest log per (candidate, qtype) and reports, per candidate:
  COMPOUND (3 paraphrases): maj-YES per cell + core (hit+near) consistency. The gate:
    - hit  maj-YES high  : the model can DETECT the compound when asked (else candidate dead)
    - near maj-YES low   : the DECISIVE near-miss discrimination works (the threshold/cutoff/
                           Rx distinction is judged correctly when the rule/question supplies it)
    - form maj-YES low   : B-only doesn't fake the compound
    - core consistency   : >=90% (paraphrase-stable labels — the load-bearing prerequisite)
  compA (1 paraphrase): component A near-ceiling on its positive cells (hit+near), low elsewhere.
  compB (1 paraphrase): component B near-ceiling on its positive cells (hit+form), low elsewhere.

A candidate that passes graduates to the keeper build; one that fails after a wording fix is
a boundary datapoint (a result), not a keeper. Gate scored greedy here (T=0), same as GPU.
Usage: python observe_ladder_screen.py
"""

import glob
import json
from collections import Counter

from inspect_ai.log import read_eval_log

from make_ladder_screen import CANDIDATES, CELLS, POSITIVE

K = 3  # compound paraphrases

# map dataset filename -> newest log path
logs: dict[str, str] = {}
for p in sorted(glob.glob("logs/*.eval")):
    try:
        dp = (read_eval_log(p, header_only=True).eval.task_args or {}).get("dataset_path", "")
    except Exception:
        continue
    name = dp.split("/")[-1]
    if name.startswith("ladder_screen_"):
        logs[name] = p  # ascending sort => newest wins


def answers_for(fname: str) -> dict[str, str]:
    """item_id -> YES/NO/UNCLEAR for a single eval file."""
    from markers import classify
    out: dict[str, str] = {}
    for s in read_eval_log(logs[fname]).samples:
        out[str(s.id)] = classify(s.output.completion or "", "YES", "NO")
    return out


def cell_of(item_id: str) -> str:
    return item_id.split("_")[-2]


print("Move 4 ladder screen — probeability gate\n" + "=" * 60)
summary = []
for cand, spec in CANDIDATES.items():
    rung, fam = spec["rung"], spec["family"]
    needed = ([f"ladder_screen_{cand}_compound_p{k}.json" for k in range(1, K + 1)]
              + [f"ladder_screen_{cand}_compA.json", f"ladder_screen_{cand}_compB.json"])
    missing = [f for f in needed if f not in logs]
    if missing:
        print(f"\n### {cand} [{rung}/{fam}]: SKIPPED — missing {[m.split('_')[-1] for m in missing]}")
        continue

    # compound: collect per-item answers across paraphrases
    comp: dict[str, list[str]] = {}
    for k in range(1, K + 1):
        for iid, ans in answers_for(f"ladder_screen_{cand}_compound_p{k}.json").items():
            comp.setdefault(iid, []).append(ans)
    cell_ids = {c: sorted(i for i in comp if cell_of(i) == c) for c in CELLS}

    def maj_yes(ids):
        return sum(Counter(comp[i])["YES"] * 2 > K for i in ids) / max(len(ids), 1)

    def unanim(ids):
        return sum(len(set(comp[i])) == 1 and comp[i][0] != "UNCLEAR" for i in ids) / max(len(ids), 1)

    print(f"\n### {cand}  [{rung} / {fam}]")
    print(f"  COMPOUND maj-YES:  " + "  ".join(f"{c}={maj_yes(cell_ids[c]):.0%}" for c in CELLS))
    core = cell_ids["hit"] + cell_ids["near"]
    consistency = unanim(core)
    hit_y, near_y, form_y = maj_yes(cell_ids["hit"]), maj_yes(cell_ids["near"]), maj_yes(cell_ids["form"])

    # components (single paraphrase)
    a_ans = answers_for(f"ladder_screen_{cand}_compA.json")
    b_ans = answers_for(f"ladder_screen_{cand}_compB.json")

    def yes_rate(ans, cells):
        ids = [i for i in ans if cell_of(i) in cells]
        return sum(ans[i] == "YES" for i in ids) / max(len(ids), 1)

    a_pos = yes_rate(a_ans, POSITIVE["compA"])          # hit+near should be YES
    a_neg = yes_rate(a_ans, set(CELLS) - POSITIVE["compA"])
    b_pos = yes_rate(b_ans, POSITIVE["compB"])          # hit+form should be YES
    b_neg = yes_rate(b_ans, set(CELLS) - POSITIVE["compB"])
    print(f"  compA (is-A):      pos(hit+near)={a_pos:.0%}  neg(form+none)={a_neg:.0%}")
    print(f"  compB (is-B):      pos(hit+form)={b_pos:.0%}  neg(near+none)={b_neg:.0%}")

    gates = {
        "hit-detect>=85%": hit_y >= 0.85,
        "near-falsefire<=20%": near_y <= 0.20,
        "form-falsefire<=20%": form_y <= 0.20,
        "core-consistency>=90%": consistency >= 0.90,
        "compA-pos>=85%": a_pos >= 0.85,
        "compB-pos>=85%": b_pos >= 0.85,
    }
    print(f"  core consistency={consistency:.0%}")
    verdict = "PASS" if all(gates.values()) else "REVIEW"
    fails = [g for g, ok in gates.items() if not ok]
    print(f"  -> {verdict}" + (f"  (check: {', '.join(fails)})" if fails else ""))
    summary.append((cand, rung, fam, verdict, hit_y, near_y, consistency, a_pos, b_pos))

print("\n" + "=" * 60 + "\nSUMMARY (cand | rung | hit | near | consist | A+ | B+ | verdict)")
for cand, rung, fam, verdict, hit_y, near_y, cons, ap, bp in summary:
    print(f"  {cand:20s} {rung}  hit={hit_y:.0%} near={near_y:.0%} "
          f"cons={cons:.0%} A+={ap:.0%} B+={bp:.0%}  {verdict}")
print("\nNote: near maj-YES is the KEY R3 read — low means the decisive element is judged")
print("correctly WHEN ASKED (probeable); the experiment then asks whether it's read WITHOUT being asked.")
