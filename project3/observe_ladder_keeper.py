"""Move 4 keeper re-screen — per-candidate probeability gate on the EXPANDED ask files
(ladder_<cand>_ask_*). Same gate as observe_ladder_screen.py but at keeper scale
(24 hit / 24 near / 16 form / 16 none). Flags the specific items that misfire so they
can be fixed or dropped before GPU extraction. Usage: python observe_ladder_keeper.py
"""
import glob
from collections import Counter

from inspect_ai.log import read_eval_log
from markers import classify
from make_ladder_screen import CANDIDATES

K = 3
CELLS = ["hit", "near", "form", "none"]
POSITIVE = {"compound": {"hit"}, "compA": {"hit", "near"}, "compB": {"hit", "form"}}

logs = {}
for p in sorted(glob.glob("logs/*.eval")):
    try:
        dp = (read_eval_log(p, header_only=True).eval.task_args or {}).get("dataset_path", "")
    except Exception:
        continue
    name = dp.split("/")[-1]
    if name.startswith("ladder_") and "_ask_" in name:
        logs[name] = p


def answers(fname):
    out = {}
    for s in read_eval_log(logs[fname]).samples:
        out[str(s.id)] = classify(s.output.completion or "", "YES", "NO")
    return out


def cell_of(i):
    return i.split("_")[-2]


summary = []
for cand, spec in CANDIDATES.items():
    need = [f"ladder_{cand}_ask_compound_p{k}.json" for k in range(1, K + 1)] + \
           [f"ladder_{cand}_ask_compA.json", f"ladder_{cand}_ask_compB.json"]
    if any(f not in logs for f in need):
        print(f"\n### {cand}: SKIPPED (missing logs)")
        continue
    comp = {}
    for k in range(1, K + 1):
        for i, a in answers(f"ladder_{cand}_ask_compound_p{k}.json").items():
            comp.setdefault(i, []).append(a)
    cids = {c: sorted(i for i in comp if cell_of(i) == c) for c in CELLS}
    mY = lambda ids: sum(Counter(comp[i])["YES"] * 2 > K for i in ids) / max(len(ids), 1)
    un = lambda ids: sum(len(set(comp[i])) == 1 and comp[i][0] != "UNCLEAR" for i in ids) / max(len(ids), 1)
    hit_y, near_y, form_y = mY(cids["hit"]), mY(cids["near"]), mY(cids["form"])
    cons = un(cids["hit"] + cids["near"])
    a_ans, b_ans = answers(f"ladder_{cand}_ask_compA.json"), answers(f"ladder_{cand}_ask_compB.json")
    yr = lambda ans, cells: (lambda ids: sum(ans[i] == "YES" for i in ids) / max(len(ids), 1))(
        [i for i in ans if cell_of(i) in cells])
    a_pos, b_pos = yr(a_ans, POSITIVE["compA"]), yr(b_ans, POSITIVE["compB"])

    print(f"\n### {cand} [{spec['rung']}/{spec['family']}]")
    print(f"  compound maj-YES: hit={hit_y:.0%} near={near_y:.0%} form={form_y:.0%} none={mY(cids['none']):.0%}"
          f"   consistency={cons:.0%}")
    print(f"  compA pos={a_pos:.0%}   compB pos={b_pos:.0%}")
    # name the misfiring items (majority-wrong on compound)
    bad_near = [i for i in cids["near"] if Counter(comp[i])["YES"] * 2 > K]
    bad_form = [i for i in cids["form"] if Counter(comp[i])["YES"] * 2 > K]
    miss_hit = [i for i in cids["hit"] if Counter(comp[i])["YES"] * 2 <= K]
    if bad_near: print(f"  near false-fire items: {[i.split('_')[-1] for i in bad_near]}")
    if bad_form: print(f"  form false-fire items: {[i.split('_')[-1] for i in bad_form]}")
    if miss_hit: print(f"  hit MISS items: {[i.split('_')[-1] for i in miss_hit]}")
    gates = (hit_y >= 0.90, near_y <= 0.12, form_y <= 0.15, cons >= 0.90, a_pos >= 0.90, b_pos >= 0.90)
    print(f"  -> {'PASS' if all(gates) else 'REVIEW'}")
    summary.append((cand, spec["rung"], hit_y, near_y, form_y, cons, a_pos, b_pos, all(gates)))

print("\n" + "=" * 64)
for cand, rung, h, n, f, c, ap, bp, ok in summary:
    print(f"  {cand:20s} {rung}  hit={h:.0%} near={n:.0%} form={f:.0%} cons={c:.0%} "
          f"A+={ap:.0%} B+={bp:.0%}  {'PASS' if ok else 'REVIEW'}")
