"""watchlist_v4 — v3 with CLEAN UNIT NAMES (review fix M2; probe-ready dataset).

v3's units were "the Nth X" (e.g. "the 3rd Frontier Company"), which caused two problems the
data review flagged:
  (a) near-duplicate stems — "the 3rd Frontier Company" vs "the 15th Frontier Company" share
      "Frontier Company", so units were the hardest/most-ambiguous type AND gave a future
      probe a "watchlisted *stem* is present" shortcut (the surface co-occurrence we want to
      defeat); and
  (b) the ordinal digit leaked into the document's numbers — the present->absent string-swap
      changed a number too, so unit pairs differed in more than the one trigger token (21/72
      v3 pairs) and mildly biased the MAX/AVG competing rules.

v4 fixes both by giving units distinctive, NON-NUMERIC codenames ("Ironside Detachment",
"Cobalt Squadron", …) — each with a unique first word, matching the decorrelation quality of
the location/person pools. Everything else is identical to v3 (same templates, decorrelation
guards, doc/watchlist knobs). This is the dataset the cross-pass probe should run on.

Output: inputs/watchlist_v4_ask.json  (derive loaded/swap controls from it as for v3:
  make_keyphrase_loaded.py --ask-in inputs/watchlist_v4_ask.json --out-prefix inputs/watchlist_v4 ...
  make_keyphrase_swapwl.py  after pointing ASK_IN at the v4 ask set)

Usage:
  python make_dataset_keyphrase_v4.py
"""

from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path

from make_dataset_v2 import audit
from make_dataset_keyphrase_v2 import TEMPLATES, ASK_SYSTEM, ASK_USER

# Units now read like locations/persons: a distinctive (unique) first word + a unit noun, NO
# digits and NO shared descriptor stems. Locations and persons are unchanged from v3.
V4_ENTITIES = {
    "unit": [
        "Ironside Detachment", "Cobalt Squadron", "Redwall Brigade", "Tideguard Flotilla",
        "Stormguard Battery", "Blackthorn Regiment", "Ravenscar Company", "Stonefield Wing",
        "Grimwald Column", "Ashmoor Division", "Brightlance Cohort", "Thorngate Vanguard",
        "Frostwood Battalion", "Emberfell Garrison", "Duskhollow Legion", "Wolfsbane Corps",
        "Silvercrest Detachment", "Hawkridge Squadron", "Mossgate Brigade", "Drakemoor Flotilla",
        "Vaultwood Battery", "Greycairn Regiment", "Oakshield Company", "Pyrebrand Wing",
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

ALL_ENTITIES = [e for lst in V4_ENTITIES.values() for e in lst]


def check_no_substring_entities() -> None:
    for a in ALL_ENTITIES:
        for b in ALL_ENTITIES:
            if a != b and a in b:
                raise SystemExit(f"ENTITY OVERLAP: '{a}' is a substring of '{b}'. Fix V4_ENTITIES.")


def build_pairs() -> list[tuple[str, str, str, int]]:
    per_type = {t: [(t, e[i], e[(i + 1) % len(e)], i) for i in range(len(e))] for t, e in V4_ENTITIES.items()}
    pairs, types = [], list(per_type)
    for r in range(max(len(v) for v in per_type.values())):
        for t in types:
            if r < len(per_type[t]):
                pairs.append(per_type[t][r])
    return pairs


def make_pair_records(rng: random.Random, idx: int, etype: str, present: str, absent: str, i: int,
                      wl_min: int, wl_max: int, doc_min: int, doc_max: int) -> list[dict]:
    pool = [e for e in V4_ENTITIES[etype] if e not in (present, absent)]
    list_size = rng.randint(doc_min, min(doc_max, len(pool) + 1))
    distractors = rng.sample(pool, list_size - 1)

    slots = distractors[:]
    slots.insert(rng.randint(0, len(slots)), present)
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
            "framing": "ask", "geometry": "watchlist_v4_cleanunits"}
    records = []
    for term, doc, label, variant, suffix in [(present, present_doc, 1, "present", "a"),
                                              (absent, absent_doc, 0, "absent", "b")]:
        records.append({
            "id": f"w4_{idx:04d}{suffix}",
            "label": label,
            "label_name": "escalate" if label == 1 else "proceed",
            "group": etype,
            "system": ASK_SYSTEM.format(watchlist=wl_str),
            "user": ASK_USER.format(doc=doc),
            "meta": {**base, "item": term, "term": term, "variant": variant, "trigger_present": label == 1},
        })
    return records


def verify(records: list[dict]) -> None:
    by_pair: dict[int, dict] = {}
    for r in records:
        doc = r["user"]
        wl, term = r["meta"]["watchlist"], r["meta"]["term"]
        in_doc = [e for e in ALL_ENTITIES if e in doc]
        if term not in in_doc:
            raise SystemExit(f"{r['id']}: trigger '{term}' not in document")
        if len(in_doc) < min(10, r["meta"]["list_size"]):
            raise SystemExit(f"{r['id']}: only {len(in_doc)} names in document")
        hits = [e for e in wl if e in doc]
        if r["label"] == 1 and hits != [term]:
            raise SystemExit(f"{r['id']}: present but watchlist-in-doc {hits} != [{term}]")
        if r["label"] == 0 and hits:
            raise SystemExit(f"{r['id']}: absent but watchlist names {hits} appear in document")
        by_pair.setdefault(r["meta"]["pair"], {})[r["meta"]["variant"]] = r
    # NEW invariant (the M2 fix): the present/absent docs must contain the SAME numbers —
    # i.e. no digit leaks in via the swapped name (v3's "the Nth X" units broke this on 21/72
    # pairs). With non-numeric names the only difference is the trigger token itself.
    for pid, halves in by_pair.items():
        p, a = halves["present"], halves["absent"]
        if sorted(re.findall(r"\d+", p["user"])) != sorted(re.findall(r"\d+", a["user"])):
            raise SystemExit(f"pair {pid}: doc numbers differ within the pair (a name leaked a digit)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-pairs", type=int, default=None)
    ap.add_argument("--wl-min", type=int, default=4)
    ap.add_argument("--wl-max", type=int, default=6)
    ap.add_argument("--doc-min", type=int, default=10)
    ap.add_argument("--doc-max", type=int, default=14)
    ap.add_argument("--out", default="inputs/watchlist_v4_ask.json")
    args = ap.parse_args()

    check_no_substring_entities()
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
    print(f"Wrote {out}  ({len(pairs)} pairs, {len(records)} items, clean unit names)")
    print(f"list sizes: {sorted({r['meta']['list_size'] for r in records})}")
    print("\nBalance audit (present=escalate / absent=proceed):")
    audit(records)


if __name__ == "__main__":
    main()
