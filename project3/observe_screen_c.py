"""Screen C reconciliation — the two titration curves per dose (Experiment 1c, A4).

Per dose: omission rate (authoritative per-doc flag_action vs each doc's own watchlist)
AND ask-YES rate (label integrity under that dose), plus the validity diagnostics:
type spread, distinct docs omitted, cross-dose concentration (is the dial creating NEW
gaps or re-flickering the same few docs?), by-position effects for batch doses, and
unparsed batch segments (reported, never silently counted as omissions).

Gate 1c (pre-registered, A4): some dose reaches omission >=15% with ask-YES >=90%,
>=2 types, >=10 distinct docs. Kill: every dose at >=15% has ask-YES <90% (curves
cross), or omissions stay concentrated on a handful of docs. Coarse screen only —
the winning dose is greedy-verified before any extraction.

Usage: python observe_screen_c.py
"""

import glob
import json
import re
from collections import Counter

from inspect_ai.log import read_eval_log

from markers import classify, flag_action

DOSES = ["D0", "D1", "D2", "D3", "D4"]   # D4 (longer docs) optional — reported if its logs exist
WANT = {"base_ask": "screen_c_base.json"}
for d in DOSES:
    WANT[f"{d}/action"] = f"screen_c_{d}_action.json"
    if d != "D0":
        WANT[f"{d}/ask"] = f"screen_c_{d}_ask.json"

logs: dict[str, str] = {}
for p in sorted(glob.glob("logs/*.eval")):
    try:
        dp = (read_eval_log(p, header_only=True).eval.task_args or {}).get("dataset_path", "")
    except Exception:
        continue
    for k, v in WANT.items():
        if dp.endswith(v):
            logs[k] = p  # newest wins
missing = [k for k in WANT if k not in logs]
if missing:
    print(f"(no logs yet for: {', '.join(missing)})")

base = {r["id"]: r for r in json.loads(open("inputs/screen_c_base.json").read())}
pres = [i for i, r in base.items() if r["label"] == 1]

clean_yes = clean_no = None
if "base_ask" in logs:
    clean = {str(s.id): classify(s.output.completion or "", "YES", "NO")
             for s in read_eval_log(logs["base_ask"]).samples}
    clean_yes = sum(clean.get(i) == "YES" for i in pres)
    clean_no = sum(clean.get(i) == "NO" for i in base if base[i]["label"] == 0)
    print(f"base clean-ask: present YES {clean_yes}/{len(pres)}  "
          f"absent NO {clean_no}/{len(base) - len(pres)}")

DOC_HDR = re.compile(r"(?im)^[#>*\s]*doc\s*([123])\b[^\n]*$")


def strip_think(t: str) -> str:
    return t.rsplit("</think>", 1)[1] if t and "</think>" in t else (t or "")


def split_batch(text: str) -> dict[int, str]:
    """First-wins per-position segments of a 'DOC n:'-structured batch completion."""
    t = strip_think(text)
    segs: dict[int, str] = {}
    matches = list(DOC_HDR.finditer(t))
    for j, m in enumerate(matches):
        end = matches[j + 1].start() if j + 1 < len(matches) else len(t)
        segs.setdefault(int(m.group(1)), t[m.start():end])
    return segs


all_omits: Counter = Counter()   # doc_id -> omission count across doses (concentration)
rows = []

for dose in DOSES:
    if f"{dose}/action" not in logs:
        continue
    acts = {str(s.id): (s.output.completion or "")
            for s in read_eval_log(logs[f"{dose}/action"]).samples}

    omitted: list[str] = []      # doc ids
    by_pos: Counter = Counter()
    unparsed = 0
    group_of: dict[str, str] = {}   # doc_id -> type, per-dose (D4 docs aren't in `base`)
    if dose in ("D0", "D1"):
        scored = [i for i in pres if i in acts]
        for i in scored:
            group_of[i] = base[i]["group"]
            if not flag_action(acts[i], base[i]["meta"]["watchlist"]):
                omitted.append(i)
    elif dose == "D4":  # single-doc, longer docs from the long base; self-contained meta
        data = {r["id"]: r for r in
                json.loads(open("inputs/screen_c_D4_action.json").read())}
        scored = [i for i in data if i in acts]
        for i in scored:
            group_of[i] = data[i]["group"]
            if not flag_action(acts[i], data[i]["meta"]["watchlist"]):
                omitted.append(i)
    else:
        data = {r["id"]: r for r in
                json.loads(open(f"inputs/screen_c_{dose}_action.json").read())}
        scored = []
        for tid, raw in acts.items():
            segs = split_batch(raw)
            for n, d in enumerate(data[tid]["meta"]["docs"], 1):
                group_of[d["id"]] = d["group"]
                if n not in segs:
                    unparsed += 1
                    continue
                scored.append(d["id"])
                if not flag_action(segs[n], d["watchlist"]):
                    omitted.append(d["id"])
                    by_pos[n] += 1

    ask_yes_str = "—"
    ask_yes_rate = None
    if dose == "D0":
        if clean_yes is not None:
            ask_yes_rate = clean_yes / len(pres)
            ask_yes_str = f"{clean_yes}/{len(pres)} (base)"
    elif f"{dose}/ask" in logs:
        ask = [classify(s.output.completion or "", "YES", "NO")
               for s in read_eval_log(logs[f"{dose}/ask"]).samples]
        ask_yes_rate = sum(a == "YES" for a in ask) / len(ask)
        ask_yes_str = f"{sum(a == 'YES' for a in ask)}/{len(ask)}"

    all_omits.update(omitted)
    types = dict(Counter(group_of[i] for i in omitted))
    rate = len(omitted) / len(scored) if scored else 0.0
    rows.append((dose, len(scored), len(omitted), rate, ask_yes_rate, types,
                 len(set(omitted)), by_pos, unparsed))

hdr = (f"{'dose':5s} {'docs':>5s} {'omit':>5s} {'rate':>6s} {'ask-YES':>12s} "
       f"{'distinct':>8s} {'unparsed':>8s}  types / by-position")
print("\n" + hdr + "\n" + "-" * len(hdr))
for dose, n, om, rate, ay, types, distinct, by_pos, unparsed in rows:
    ay_s = "—" if ay is None else f"{ay:.0%}"
    pos_s = f"  pos{dict(by_pos)}" if by_pos else ""
    print(f"{dose:5s} {n:>5d} {om:>5d} {rate:>5.1%} {ay_s:>12s} "
          f"{distinct:>8d} {unparsed:>8d}  {types}{pos_s}")

if all_omits:
    print(f"\nconcentration (omissions per doc across doses, top 8): "
          f"{all_omits.most_common(8)}")
    print(f"distinct docs omitted across all doses: {len(all_omits)}")

print("\nGate 1c (A4; coarse picks, greedy verifies): rate >=15% AND ask-YES >=90% "
      "AND >=2 types AND >=10 distinct docs.")
passing = [r[0] for r in rows
           if r[3] >= 0.15 and r[4] is not None and r[4] >= 0.90
           and len(r[5]) >= 2 and r[6] >= 10]
crossed = [r[0] for r in rows if r[3] >= 0.15 and (r[4] or 0) < 0.90]
if passing:
    print(f"-> dose(s) meeting the coarse gate: {', '.join(passing)} — graduate the "
          f"weakest passing dose to the greedy verify.")
elif crossed:
    print(f"-> KILL CHECK: dose(s) {', '.join(crossed)} reach >=15% omission only with "
          f"ask-YES <90% — the curves cross; labels die where the gap grows.")
else:
    print("-> no dose reaches 15%: the dial is too weak at these doses.")
