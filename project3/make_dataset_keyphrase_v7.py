"""watchlist_v7 — further SCALE-UP of the validated design (v6 doubled: 160 names/type).

v6 (80/type, 240 pairs) confirmed the phenomenon holds at scale but gave n_gap≈15 — the H5 gap
rate is ~6%, lower than the noisy ~10% v5 estimate, so we undershot the pre-registered ~24. v7
doubles the pools again (80→160/type, 240→**480 pairs**) to (a) push n_gap to ~29 at a 6% rate
and (b) pin the gap *rate* itself with a much tighter CI — i.e. test whether 6% is stable.

Design is IDENTICAL to v5/v6 (same 17 FORMATS imported from v5, same matched-pair/replace logic,
same guards). Only the entity pool grows:
  V7_ENTITIES = v6's 160... no — v6's 80/type (kept verbatim) + 80 NEW names/type = 160/type.
The 80 new tokens/type are the canonical, collision-filtered list in make_keyphrase_v7_tokens.py
(see select_v7_tokens.py for provenance), paired with the SAME cycled nouns/ranks v6 used.

Two generation guards (both must pass):
  - check_no_substring_entities(): no full name is a substring of another (the hard invariant);
  - check_distinctive_unique(): every distinctive token globally unique.

Output: inputs/watchlist_v7_ask.json  (derive load/swap exactly as v6:
  python make_keyphrase_loaded.py --load 5 --ask-in inputs/watchlist_v7_ask.json --out-prefix inputs/watchlist_v7
  python make_keyphrase_swapwl.py --ask-in inputs/watchlist_v7_ask.json)

Usage:
  python make_dataset_keyphrase_v7.py
"""

from __future__ import annotations

import argparse
import json
import random
import re
from collections import Counter
from pathlib import Path

from make_dataset_v2 import audit
from make_dataset_keyphrase_v2 import ASK_SYSTEM, ASK_USER
from make_dataset_keyphrase_v5 import FORMATS
from make_dataset_keyphrase_v6 import V6_ENTITIES, UNIT_NOUNS, LOC_NOUNS, RANKS
from make_keyphrase_v7_tokens import UNIT_CODEWORDS_V7, LOC_CODEWORDS_V7, SURNAMES_V7

# New entities assembled from the canonical v7 tokens + the SAME cycled nouns/ranks as v6.
NEW_ENTITIES = {
    "unit": [f"{c} {UNIT_NOUNS[i % len(UNIT_NOUNS)]}" for i, c in enumerate(UNIT_CODEWORDS_V7)],
    "location": [f"{c} {LOC_NOUNS[i % len(LOC_NOUNS)]}" for i, c in enumerate(LOC_CODEWORDS_V7)],
    "person": [f"{RANKS[i % len(RANKS)]} {s}" for i, s in enumerate(SURNAMES_V7)],
}
V7_ENTITIES = {t: V6_ENTITIES[t] + NEW_ENTITIES[t] for t in V6_ENTITIES}
ALL_ENTITIES = [e for lst in V7_ENTITIES.values() for e in lst]


def _distinctive(etype: str, name: str) -> str:
    return name.split()[-1] if etype == "person" else name.split()[0]


def check_no_substring_entities() -> None:
    for a in ALL_ENTITIES:
        for b in ALL_ENTITIES:
            if a != b and a in b:
                raise SystemExit(f"ENTITY OVERLAP: '{a}' is a substring of '{b}'. Fix the token lists.")


def check_distinctive_unique() -> None:
    seen: dict[str, str] = {}
    for t, lst in V7_ENTITIES.items():
        for e in lst:
            d = _distinctive(t, e)
            if d in seen:
                raise SystemExit(f"DUP distinctive token '{d}': '{seen[d]}' vs '{e}'. Fix the token lists.")
            seen[d] = e


def build_pairs() -> list[tuple[str, str, str, int]]:
    per_type = {t: [(t, e[i], e[(i + 1) % len(e)], i) for i in range(len(e))] for t, e in V7_ENTITIES.items()}
    pairs, types = [], list(per_type)
    for r in range(max(len(v) for v in per_type.values())):
        for t in types:
            if r < len(per_type[t]):
                pairs.append(per_type[t][r])
    return pairs


def make_pair_records(rng, idx, etype, present, absent, i, wl_min, wl_max, doc_min, doc_max):
    pool = [e for e in V7_ENTITIES[etype] if e not in (present, absent)]
    list_size = rng.randint(doc_min, min(doc_max, len(pool) + 1))
    distractors = rng.sample(pool, list_size - 1)

    slots = distractors[:]
    slots.insert(rng.randint(0, len(slots)), present)            # trigger at a random position
    fmt = FORMATS[idx % len(FORMATS)]                            # format decoupled from type
    present_doc = fmt(slots, rng)
    if present_doc.count(present) != 1:
        raise SystemExit(f"pair {idx}: trigger '{present}' not unique in document")
    absent_doc = present_doc.replace(present, absent)            # ONLY the one name changes

    forbidden = {present, absent, *distractors}
    pad_pool = [e for e in ALL_ENTITIES if e not in forbidden]
    wl_size = rng.randint(wl_min, wl_max)
    watchlist = rng.sample(pad_pool, wl_size - 1) + [present]
    rng.shuffle(watchlist)
    wl_str = ", ".join(watchlist)

    base = {"entity_type": etype, "watchlist": watchlist, "distractors": distractors,
            "list_size": list_size, "template": fmt.__name__, "pair": idx,
            "framing": "ask", "geometry": "watchlist_v7_diverse"}
    records = []
    for term, doc, label, variant, suffix in [(present, present_doc, 1, "present", "a"),
                                              (absent, absent_doc, 0, "absent", "b")]:
        records.append({
            "id": f"w7_{idx:04d}{suffix}",
            "label": label,
            "label_name": "escalate" if label == 1 else "proceed",
            "group": etype,
            "system": ASK_SYSTEM.format(watchlist=wl_str),
            "user": ASK_USER.format(doc=doc),
            "meta": {**base, "item": term, "term": term, "variant": variant,
                     "trigger_present": label == 1, "doc": doc},
        })
    return records


def verify(records):
    by_pair = {}
    for r in records:
        doc = r["user"]
        wl, term = r["meta"]["watchlist"], r["meta"]["term"]
        in_doc = [e for e in ALL_ENTITIES if e in doc]
        if term not in in_doc:
            raise SystemExit(f"{r['id']}: trigger '{term}' not in document")
        if len(in_doc) < min(5, r["meta"]["list_size"]):
            raise SystemExit(f"{r['id']}: only {len(in_doc)} names in document")
        hits = [e for e in wl if e in doc]
        if r["label"] == 1 and hits != [term]:
            raise SystemExit(f"{r['id']}: present but watchlist-in-doc {hits} != [{term}]")
        if r["label"] == 0 and hits:
            raise SystemExit(f"{r['id']}: absent but watchlist names {hits} appear in document")
        by_pair.setdefault(r["meta"]["pair"], {})[r["meta"]["variant"]] = r
    for pid, halves in by_pair.items():
        p, a = halves["present"], halves["absent"]
        if sorted(re.findall(r"\d+", p["user"])) != sorted(re.findall(r"\d+", a["user"])):
            raise SystemExit(f"pair {pid}: doc numbers differ within the pair")
        if p["user"].replace(p["meta"]["term"], a["meta"]["term"]) != a["user"]:
            raise SystemExit(f"pair {pid}: docs differ beyond the swapped name (formatting leak)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-pairs", type=int, default=None)
    ap.add_argument("--wl-min", type=int, default=4)
    ap.add_argument("--wl-max", type=int, default=6)
    ap.add_argument("--doc-min", type=int, default=5)
    ap.add_argument("--doc-max", type=int, default=13)
    ap.add_argument("--out", default="inputs/watchlist_v7_ask.json")
    args = ap.parse_args()

    check_no_substring_entities()
    check_distinctive_unique()
    rng = random.Random(args.seed)

    pairs = build_pairs()
    if args.max_pairs:
        pairs = pairs[:args.max_pairs]
    records = []
    for idx, (etype, present, absent, i) in enumerate(pairs):
        records.extend(make_pair_records(rng, idx, etype, present, absent, i,
                                         args.wl_min, args.wl_max, args.doc_min, args.doc_max))
    verify(records)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(records, indent=2))
    present = [r for r in records if r["label"] == 1]
    print(f"Wrote {out}  ({len(pairs)} pairs, {len(records)} items, {len(FORMATS)} formats)")
    print(f"entities/type: {({t: len(v) for t, v in V7_ENTITIES.items()})}")
    print(f"list sizes: {sorted({r['meta']['list_size'] for r in records})}")
    ft = Counter((r["meta"]["template"], r["group"]) for r in present)
    print("\nformat x type (present items) — should be spread, not type-locked:")
    for f in FORMATS:
        row = {t: ft.get((f.__name__, t), 0) for t in V7_ENTITIES}
        print(f"  {f.__name__:12s} {row}")
    print("\nBalance audit (present=escalate / absent=proceed):")
    audit(records)


if __name__ == "__main__":
    main()
