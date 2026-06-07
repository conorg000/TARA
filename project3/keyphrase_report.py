"""Report the keyphrase recognition gate (keyphrase_idea.md Step 1) from an ask log.

Step 1 has no action pass, so this is simpler than gate_report.py — but it adds the
thing that matters for matched pairs: PAIR CONSISTENCY (did both halves of a pair
answer correctly — YES on present, NO on absent). At N~80 with a 95% bar that flip
signal is stronger than the marginal rates alone.

As in gate_report, markers are RE-DERIVED from the saved completion with the
bracket-tolerant parser (not the stored score), so logs are re-scored correctly
offline. The pair id and variant are read off the sample id (kp_<idx>{a|b}); a=present
(label 1), b=absent (label 0). Misses are enriched with the term + watchlist from the
dataset JSON so they can be eyeballed (ambiguous item vs phrasing artifact).

Usage:
    ./.venv/bin/python keyphrase_report.py --ask <ask.eval> [--dataset inputs/watchlist_v1_ask.json]
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from inspect_ai.log import read_eval_log

from markers import classify


def load_dataset(path: str) -> dict:
    p = Path(path)
    if not p.is_absolute():
        p = Path(__file__).parent / p
    return {r["id"]: r for r in json.loads(p.read_text())}


def pct(n, d):
    return f"{n}/{d} = {n/d:.3f}" if d else "0/0 = —"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ask", required=True)
    ap.add_argument("--dataset", default="inputs/watchlist_v1_ask.json")
    ap.add_argument("--label", default="")
    args = ap.parse_args()

    data = load_dataset(args.dataset)
    log = read_eval_log(args.ask)

    # id -> (label, marker), re-parsed from the completion.
    rows, maxlen = {}, 0
    for s in log.samples:
        comp = s.output.completion or ""
        maxlen = max(maxlen, len(comp))
        rows[str(s.id)] = (int(s.metadata.get("label")), classify(comp, "YES", "NO"))

    present = {i: m for i, (lab, m) in rows.items() if lab == 1}
    absent = {i: m for i, (lab, m) in rows.items() if lab == 0}
    yes_present = sum(1 for m in present.values() if m == "YES")
    no_absent = sum(1 for m in absent.values() if m == "NO")
    unclear = sum(1 for _, m in rows.values() if m == "UNCLEAR")

    print(f"\n========== KEYPHRASE GATE {args.label} ==========")
    print(f"ask log: {args.ask}  (max completion len {maxlen} chars)")
    print(f"N = {len(rows)}  ({len(present)} present / {len(absent)} absent)  UNCLEAR={unclear}")
    print("\n-- RECOGNITION RATES --")
    print(f"  trigger-present -> YES : {pct(yes_present, len(present))}")
    print(f"  trigger-absent  -> NO  : {pct(no_absent, len(absent))}")

    # Pair consistency: both halves of kp_<idx> correct.
    by_pair = defaultdict(dict)  # idx -> {"a": correct?, "b": correct?}
    for i, (lab, m) in rows.items():
        idx, variant = i[:-1], i[-1]
        correct = (m == "YES") if lab == 1 else (m == "NO")
        by_pair[idx][variant] = correct
    full = sum(1 for v in by_pair.values() if v.get("a") and v.get("b"))
    print("\n-- PAIR CONSISTENCY --")
    print(f"  both halves correct (YES on present, NO on absent): {pct(full, len(by_pair))}")

    # Misses, enriched for eyeballing.
    misses = []
    for i, (lab, m) in rows.items():
        correct = (m == "YES") if lab == 1 else (m == "NO")
        if not correct:
            misses.append((i, lab, m))
    if misses:
        print(f"\n-- MISSES ({len(misses)}) --")
        for i, lab, m in sorted(misses):
            meta = data.get(i, {}).get("meta", {})
            term = meta.get("term", "?")
            wl = meta.get("watchlist", [])
            want = "YES" if lab == 1 else "NO"
            print(f"  {i}  want={want} got={m}  term='{term}'  ({meta.get('variant')}, {meta.get('entity_type')})")
            print(f"        watchlist: {wl}")
    else:
        print("\n-- MISSES (0) -- clean.")


if __name__ == "__main__":
    main()
