"""watchlist_v6 — SCALE-UP of the validated v5 design (same shapes, ~3.3x the names).

v5 proved the design: recognition holds at ceiling across all 17 document shapes and the
silent-omission gap is real and shape-general. The only weak link was n — the watchdog rested
on n_gap ~= 7-9 (directional, wide bars). v6 changes NOTHING about the design and only grows
the entity pools from 24 -> 80 per type (72 -> 240 pairs), so the gap pile scales ~3.3x to
~24, enough to put real error bars on the decisive gap-vs-flagged control.

What is identical to v5 (the load-bearing invariants — do not touch):
  - the SAME 17 type-agnostic FORMATS, imported from v5 (format decoupled from type);
  - matched pair by string-replace -> present & absent differ in EXACTLY the one name;
  - trigger is an exact-match string, appears once, among same-type distractors (membership,
    not category); cyclic pairing decorrelates identity from label;
  - clean non-numeric names, no digit leak, within-pair digit-equality;
  - verify()'s STRONG guard: present.replace(trigger, other) == absent (no format leak).

What is new: V6_ENTITIES = v4's 24/type (kept verbatim, already validated) + 56 new names/type.
The new names are assembled from hand-authored DISTINCTIVE tokens (unit/location codeword =
first word; person = surname) paired with a cycled noun/rank, so the only authoring surface is
the distinctive token list. Two guards run at generation:
  - check_no_substring_entities(): no full name is a substring of another (protects the
    replace/count/in-doc logic — the hard invariant);
  - check_distinctive_unique(): every distinctive token is globally unique (no stem shortcut).
Shared SUFFIXES (-wood, -gate, -moor, -bury, rank words) are fine — v4 has them and held.

Output: inputs/watchlist_v6_ask.json  (derive load/swap exactly as v5:
  python make_keyphrase_loaded.py --load 5 --ask-in inputs/watchlist_v6_ask.json --out-prefix inputs/watchlist_v6
  python make_keyphrase_swapwl.py --ask-in inputs/watchlist_v6_ask.json)

Usage:
  python make_dataset_keyphrase_v6.py
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
from make_dataset_keyphrase_v4 import V4_ENTITIES
from make_dataset_keyphrase_v5 import FORMATS

# --- New distinctive tokens (56/type). Units/locations: a unique codeword (first word) paired
# with a cycled noun. Persons: a unique surname paired with a cycled rank. Nouns/ranks repeat by
# design (v4 already reuses "Detachment", "Sergeant", etc.); only the codeword/surname must be
# globally unique. -----------------------------------------------------------------------------
UNIT_NOUNS = ["Detachment", "Squadron", "Brigade", "Flotilla", "Battery", "Regiment", "Company",
              "Wing", "Column", "Division", "Cohort", "Vanguard", "Battalion", "Garrison",
              "Legion", "Corps", "Platoon", "Section", "Troop", "Patrol"]
LOC_NOUNS = ["Hollow", "Station", "Ridge", "Flats", "Basin", "Crossing", "Point", "Reach",
             "Wharf", "Quarter", "Depot", "Yard", "Siding", "Junction", "Cutting", "Common",
             "Spur", "Bank", "Bridge", "Halt"]
RANKS = ["Sergeant", "Corporal", "Lieutenant", "Private", "Captain", "Major", "Colonel", "Ensign"]

UNIT_CODEWORDS = [
    "Crownvale", "Stagmoor", "Brackenhill", "Coppervein", "Saltspire", "Glasswater", "Ambercliff",
    "Hollowmere", "Ravenhall", "Thistledown", "Nightforge", "Sablewood", "Gildenreach",
    "Marrowstone", "Foxglove", "Cindermoor", "Bramblewick", "Hartfell", "Larkspur", "Quillon",
    "Westvane", "Northgale", "Brindlemark", "Cresthollow", "Dawnreach", "Fenmoor", "Garrowmere",
    "Hexford", "Inglewood", "Jasperfield", "Kindleforge", "Lockridge", "Mournvale", "Norwick",
    "Oxholm", "Pendrake", "Quarrydale", "Roanwood", "Sternhollow", "Tarnbrook", "Veilstone",
    "Wickmoor", "Yarrowfield", "Zephyrhall", "Briarhost", "Crowmoor", "Dunhallow", "Elderwick",
    "Farrowgate", "Gravenhurst", "Hadrumere", "Ironvault", "Kelmarsh", "Loxley", "Vantmoor",
    "Penrith",
]
LOC_CODEWORDS = [
    "Veldon", "Marris", "Caulfield", "Tannock", "Pelham", "Wrenley", "Dunkeld", "Faxton",
    "Garmond", "Helby", "Iverness", "Jarrow", "Kelridge", "Loften", "Maybeck", "Norden",
    "Ossett", "Padbury", "Quenby", "Radwell", "Selby", "Tarbet", "Ulverstone", "Vexley",
    "Watton", "Yelden", "Ashby", "Branton", "Cawdor", "Denholm", "Elloughton", "Felgate",
    "Wexbridge", "Hethers", "Ilkmoor", "Jevington", "Kirby", "Larden", "Marsden", "Nuthall",
    "Otterburn", "Penkridge", "Quoyle", "Ravensden", "Skelton", "Throop", "Uffington", "Vobster",
    "Walberton", "Yapton", "Edderton", "Linbridge", "Glentham", "Hubberholme", "Inkpen",
    "Kelfield",
]
SURNAMES = [
    "Ashworth", "Buckley", "Castellano", "Driscoll", "Ellingham", "Farraday", "Gallagher",
    "Hartwell", "Ibarra", "Jevons", "Kowalski", "Langford", "Mahoney", "Nicholson", "Ottoway",
    "Prescott", "Quigley", "Radcliffe", "Stanhope", "Thornbury", "Underwood", "Voss", "Wakefield",
    "Yates", "Beaumont", "Cavanagh", "Delacroix", "Easton", "Fairbanks", "Grimshaw", "Hollings",
    "Iverson", "Jennings", "Kirkpatrick", "Lockwood", "Maddox", "Newbury", "Ohlsson", "Pemberton",
    "Quintero", "Ramsey", "Sheridan", "Tennant", "Ulrich", "Verity", "Whitmore", "Yarbrough",
    "Ackerley", "Bracewell", "Coltrane", "Donovan", "Esposito", "Fitzgerald", "Sefton", "Hewson",
    "Jardine",
]

NEW_ENTITIES = {
    "unit": [f"{c} {UNIT_NOUNS[i % len(UNIT_NOUNS)]}" for i, c in enumerate(UNIT_CODEWORDS)],
    "location": [f"{c} {LOC_NOUNS[i % len(LOC_NOUNS)]}" for i, c in enumerate(LOC_CODEWORDS)],
    "person": [f"{RANKS[i % len(RANKS)]} {s}" for i, s in enumerate(SURNAMES)],
}
V6_ENTITIES = {t: V4_ENTITIES[t] + NEW_ENTITIES[t] for t in V4_ENTITIES}
ALL_ENTITIES = [e for lst in V6_ENTITIES.values() for e in lst]


def _distinctive(etype: str, name: str) -> str:
    """The token that must be globally unique: surname (last word) for persons, codeword
    (first word) for units/locations."""
    return name.split()[-1] if etype == "person" else name.split()[0]


def check_no_substring_entities() -> None:
    for a in ALL_ENTITIES:
        for b in ALL_ENTITIES:
            if a != b and a in b:
                raise SystemExit(f"ENTITY OVERLAP: '{a}' is a substring of '{b}'. Fix the token lists.")


def check_distinctive_unique() -> None:
    seen: dict[str, str] = {}
    for t, lst in V6_ENTITIES.items():
        for e in lst:
            d = _distinctive(t, e)
            if d in seen:
                raise SystemExit(f"DUP distinctive token '{d}': '{seen[d]}' vs '{e}'. Fix the token lists.")
            seen[d] = e


def build_pairs() -> list[tuple[str, str, str, int]]:
    """Cyclic pairing per type (each entity is trigger once and non-trigger once -> identity is
    orthogonal to label), interleaved across types for index-balance. Same as v4/v5."""
    per_type = {t: [(t, e[i], e[(i + 1) % len(e)], i) for i in range(len(e))] for t, e in V6_ENTITIES.items()}
    pairs, types = [], list(per_type)
    for r in range(max(len(v) for v in per_type.values())):
        for t in types:
            if r < len(per_type[t]):
                pairs.append(per_type[t][r])
    return pairs


def make_pair_records(rng, idx, etype, present, absent, i, wl_min, wl_max, doc_min, doc_max):
    pool = [e for e in V6_ENTITIES[etype] if e not in (present, absent)]
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
            "framing": "ask", "geometry": "watchlist_v6_diverse"}
    records = []
    for term, doc, label, variant, suffix in [(present, present_doc, 1, "present", "a"),
                                              (absent, absent_doc, 0, "absent", "b")]:
        records.append({
            "id": f"w6_{idx:04d}{suffix}",
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
    ap.add_argument("--out", default="inputs/watchlist_v6_ask.json")
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
    print(f"entities/type: {({t: len(v) for t, v in V6_ENTITIES.items()})}")
    print(f"list sizes: {sorted({r['meta']['list_size'] for r in records})}")
    ft = Counter((r["meta"]["template"], r["group"]) for r in present)
    print("\nformat x type (present items) — should be spread, not type-locked:")
    for f in FORMATS:
        row = {t: ft.get((f.__name__, t), 0) for t in V6_ENTITIES}
        print(f"  {f.__name__:12s} {row}")
    print("\nBalance audit (present=escalate / absent=proceed):")
    audit(records)


if __name__ == "__main__":
    main()
