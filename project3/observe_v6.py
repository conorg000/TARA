"""Observe the v6 (scale-up) behaviour on OpenRouter — does recognition stay at ceiling and the
silent-omission gap hold its ~10% rate at 3.3x the names (240 pairs), before we spend GPU?

Identical reconciliation to observe_v5.py, pointed at the v6 datasets. Gap = present, recognised
under load (loaded-ask YES), but the action pass emitted no authoritative FLAG (flag_action with
the item's own watchlist). Breaks the gap down by format/type to confirm it stays shape-general.

Usage: python observe_v6.py
"""
import glob
import json
from collections import Counter

from inspect_ai.log import read_eval_log
from markers import classify, flag_action

data = {r["id"]: r for r in json.loads(open("inputs/watchlist_v6_ask.json").read())}
WANT = {
    "ask": "watchlist_v6_ask.json",
    "loadedask": "watchlist_v6_loadedask_H5.json",
    "swap": "watchlist_v6_swapwl_ask.json",
    "action": "watchlist_v6_action_H5.json",
}

# newest log per target dataset (filenames are ISO-timestamped, so sorted() ascending -> newest last)
logs = {}
for p in sorted(glob.glob("logs/*.eval")):
    try:
        dp = (read_eval_log(p, header_only=True).eval.task_args or {}).get("dataset_path", "")
    except Exception:
        continue
    for k, v in WANT.items():
        if dp.endswith(v):
            logs[k] = p
missing = [k for k in WANT if k not in logs]
if missing:
    raise SystemExit(f"missing logs for {missing} — has the gate run finished?")
print("using logs:")
for k in WANT:
    print(f"  {k:10s} {logs[k]}")


def answers(path, pos, neg):
    return {str(s.id): classify(s.output.completion or "", pos, neg) for s in read_eval_log(path).samples}


ask = answers(logs["ask"], "YES", "NO")
lda = answers(logs["loadedask"], "YES", "NO")
swap = answers(logs["swap"], "YES", "NO")
actcomp = {str(s.id): (s.output.completion or "") for s in read_eval_log(logs["action"]).samples}
acthit = {i: flag_action(actcomp.get(i, ""), data[i]["meta"]["watchlist"]) for i in data}

pres = [i for i in data if i.endswith("a")]
absent = [i for i in data if i.endswith("b")]


def rate(label, n, d):
    print(f"  {label:34s} {n}/{d}  ({n/d:.0%})")


print("\n=== RECOGNITION (does it stay at ceiling at the bigger n?) ===")
rate("ASK present-YES", sum(ask.get(i) == "YES" for i in pres), len(pres))
rate("ASK absent-NO", sum(ask.get(i) == "NO" for i in absent), len(absent))
rate("LOADED-ASK present-YES (under load)", sum(lda.get(i) == "YES" for i in pres), len(pres))
rate("SWAP NO (membership dark)", sum(v == "NO" for v in swap.values()), len(swap))

print("\n=== ACTION ===")
rate("present FLAG-hit", sum(acthit[i] for i in pres), len(pres))
rate("absent over-flag", sum(acthit[i] for i in absent), len(absent))

gap = sorted(i for i in pres if lda.get(i) == "YES" and not acthit[i])
miss = sorted(i for i in pres if lda.get(i) == "NO")
print("\n=== THE GAP (present, recognised under load, but no FLAG) ===")
print(f"  gap n = {len(gap)}   ({len(gap)/len(pres):.0%} of present)   (recognition-miss under load n = {len(miss)})")
print(f"  gap by TYPE   : {dict(Counter(data[i]['group'] for i in gap))}")
print(f"  gap by FORMAT : {dict(Counter(data[i]['meta']['template'] for i in gap))}")
print(f"  gap ids: {gap}")

print("\n=== recognition (ASK present-YES) by FORMAT — should be ~all 1.0 if shapes are readable ===")
tot = Counter(data[i]["meta"]["template"] for i in pres)
yes = Counter(data[i]["meta"]["template"] for i in pres if ask.get(i) == "YES")
for f in sorted(tot):
    flag = "" if yes[f] == tot[f] else "   <-- dip"
    print(f"  {f:12s} {yes[f]}/{tot[f]}{flag}")
