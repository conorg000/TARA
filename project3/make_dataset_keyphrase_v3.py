"""watchlist_v3 — LONG mundane documents for the heavy-load sweep (keyphrase Step 2a, v3).

Same crisp trigger, trustworthy label and decorrelation guards as v2, with two changes that
serve the load push (see keyphrase_step2.md / chat 2026-06-07):

  1. **Longer documents (the reserved length lever).** Each record now lists 10–14 same-type
     entities (v2 had 3–5), with the watchlist name buried mid-list among many distractors —
     more findability pressure, and enough line items that a competing "if >8 items..." rule
     always fires under load.
  2. **Bigger entity pools (24 per type, scale-up).** Supports the long docs without
     exhausting a type, and ~72 matched pairs (144 items) for a usable gap pile.

This file emits only the CLEAN ask (recognition baseline on the harder documents). The
loaded action and loaded-ask sets are derived from it by make_keyphrase_loaded.py, so all
three framings share documents/watchlists/ids.

Output:
  inputs/watchlist_v3_ask.json          (full)
  inputs/watchlist_v3_pilot_ask.json    (--max-pairs 6)

Usage:
  python make_dataset_keyphrase_v3.py
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from make_dataset_v2 import audit
from make_dataset_keyphrase_v2 import TEMPLATES, ASK_SYSTEM, ASK_USER

# 24 entities per type (v2's 15 + 9). Same-type names are interchangeable in a list; the
# present<->absent swap reads naturally and the in-document distractors are plausible.
V3_ENTITIES = {
    "unit": [
        "the 3rd Frontier Company", "the 4th Meridian Brigade", "the 12th Coastal Wing",
        "the 9th Signals Battalion", "the 2nd Engineering Regiment", "the 8th Transport Column",
        "the 7th Highland Battalion", "the 5th Mountain Division", "the 18th Artillery Battery",
        "the 6th Garrison Company", "the 11th Recon Squadron", "the 14th Supply Wing",
        "Ironside Detachment", "Tideguard Flotilla", "Cobalt Squadron",
        "the 15th Frontier Company", "the 21st Coastal Wing", "the 6th Signals Battalion",
        "the 10th Transport Column", "the 1st Highland Battalion", "the 17th Artillery Battery",
        "the 13th Recon Squadron", "Redwall Detachment", "Stormguard Flotilla",
    ],
    "location": [
        "Orsk Hollow", "Bellweather Station", "Drennan Ridge", "Kessler Flats", "Vornid Basin",
        "Tamlin Crossing", "Mereth Point", "Calder Reach", "Sundby Wharf", "Renholm Quarter",
        "Harlow Depot", "Aldermoor Yard", "Pinehurst Siding", "Westmark Gate", "Caldridge Halt",
        "Eastgate Yard", "Marlow Crossing", "Brackish Point", "Dunmore Ridge", "Holloway Depot",
        "Saltmarsh Halt", "Greywater Basin", "Thornton Reach", "Castleford Siding",
    ],
    "person": [
        "Sergeant Halloran", "Corporal Devereux", "Lieutenant Mowbray", "Private Ashcombe",
        "Sergeant Fenwick", "Corporal Rutherford", "Lieutenant Brennan", "Private Carrow",
        "Sergeant Lindqvist", "Corporal Vasquez", "Lieutenant Okafor", "Private Mercer",
        "Sergeant Daugherty", "Corporal Whitlock", "Lieutenant Pakenham",
        "Captain Ridley", "Major Pennington", "Sergeant Calloway", "Corporal Hewitt",
        "Lieutenant Sorenson", "Private Aldridge", "Captain Mallory", "Major Trevino",
        "Sergeant Nakamura",
    ],
}

ALL_ENTITIES = [e for lst in V3_ENTITIES.values() for e in lst]


def check_no_substring_entities() -> None:
    for a in ALL_ENTITIES:
        for b in ALL_ENTITIES:
            if a != b and a in b:
                raise SystemExit(f"ENTITY OVERLAP: '{a}' is a substring of '{b}'. Fix V3_ENTITIES.")


def build_pairs() -> list[tuple[str, str, str, int]]:
    """Cyclic pairing per type; round-robin interleave so any prefix spans all three types."""
    per_type = {t: [(t, e[i], e[(i + 1) % len(e)], i) for i in range(len(e))] for t, e in V3_ENTITIES.items()}
    pairs, types = [], list(per_type)
    for r in range(max(len(v) for v in per_type.values())):
        for t in types:
            if r < len(per_type[t]):
                pairs.append(per_type[t][r])
    return pairs


def make_pair_records(rng: random.Random, idx: int, etype: str, present: str, absent: str, i: int,
                      wl_min: int, wl_max: int) -> list[dict]:
    pool = [e for e in V3_ENTITIES[etype] if e not in (present, absent)]
    list_size = rng.randint(10, 14)
    distractors = rng.sample(pool, list_size - 1)

    slots = distractors[:]
    slots.insert(rng.randint(0, len(slots)), present)  # trigger buried mid-list
    template = TEMPLATES[etype][i % len(TEMPLATES[etype])]
    present_doc = template(slots, rng)
    if present_doc.count(present) != 1:
        raise SystemExit(f"pair {idx}: trigger '{present}' not unique in document")
    absent_doc = present_doc.replace(present, absent)

    forbidden = {present, absent, *distractors}
    pad_pool = [e for e in ALL_ENTITIES if e not in forbidden]
    wl_size = rng.randint(wl_min, wl_max)
    watchlist = rng.sample(pad_pool, wl_size - 1) + [present]
    rng.shuffle(watchlist)
    wl_str = ", ".join(watchlist)

    base = {"entity_type": etype, "watchlist": watchlist, "distractors": distractors,
            "list_size": list_size, "template": template.__name__, "pair": idx,
            "framing": "ask", "geometry": "watchlist_v3_longdoc"}
    records = []
    for term, doc, label, variant, suffix in [(present, present_doc, 1, "present", "a"),
                                              (absent, absent_doc, 0, "absent", "b")]:
        records.append({
            "id": f"w3_{idx:04d}{suffix}",
            "label": label,
            "label_name": "escalate" if label == 1 else "proceed",
            "group": etype,
            "system": ASK_SYSTEM.format(watchlist=wl_str),
            "user": ASK_USER.format(doc=doc),
            "meta": {**base, "item": term, "term": term, "variant": variant, "trigger_present": label == 1},
        })
    return records


def verify(records: list[dict]) -> None:
    for r in records:
        doc = r["user"]
        wl, term = r["meta"]["watchlist"], r["meta"]["term"]
        in_doc = [e for e in ALL_ENTITIES if e in doc]
        if term not in in_doc:
            raise SystemExit(f"{r['id']}: trigger '{term}' not in document")
        if len(in_doc) < 10:
            raise SystemExit(f"{r['id']}: only {len(in_doc)} names (need >=10 for the long-doc load)")
        hits = [e for e in wl if e in doc]
        if r["label"] == 1 and hits != [term]:
            raise SystemExit(f"{r['id']}: present but watchlist-in-doc {hits} != [{term}]")
        if r["label"] == 0 and hits:
            raise SystemExit(f"{r['id']}: absent but watchlist names {hits} appear in document")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-pairs", type=int, default=None)
    ap.add_argument("--wl-min", type=int, default=4, help="min watchlist size")
    ap.add_argument("--wl-max", type=int, default=6, help="max watchlist size")
    ap.add_argument("--out", default="inputs/watchlist_v3_ask.json")
    args = ap.parse_args()

    check_no_substring_entities()
    rng = random.Random(args.seed)

    pairs = build_pairs()
    if args.max_pairs:
        pairs = pairs[:args.max_pairs]
    records = []
    for idx, (etype, present, absent, i) in enumerate(pairs):
        records.extend(make_pair_records(rng, idx, etype, present, absent, i, args.wl_min, args.wl_max))
    verify(records)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(records, indent=2))
    print(f"Wrote {out}  ({len(pairs)} pairs, {len(records)} items, long docs)")
    print(f"list sizes: {sorted({r['meta']['list_size'] for r in records})}  "
          f"| pairs by type: {({t: sum(1 for r in records if r['group']==t and r['label']==1) for t in V3_ENTITIES})}")
    print("\nBalance audit (present=escalate / absent=proceed):")
    audit(records)


if __name__ == "__main__":
    main()
