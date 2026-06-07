"""Generate watchlist_v2 — MUNDANE-RECORD keyphrase trigger (redesigned documents).

Fixes the confound in watchlist_v1: those documents announced importance ("flagged for
immediate attention", "key party of interest"), so the model could flag on tone without
checking the watchlist. Under load it did exactly that — flagging any salient name (runlog
2026-06-07 Step 2a). v2 removes the tell.

PRINCIPLE (per the design brief): the document is a boring routine record. The watchlist
name sits in it as one ordinary entry among several of the same type. Nothing about the
document says "important". The only path to the right answer is to check each listed name
against the watchlist.

  - Mundane templates: supply allocations, duty rosters, maintenance logs, transport
    manifests, attendance sheets, etc. Each lists 3-5 same-type entities with boring numeric
    / scheduling detail. Templates rotate so the probe can't key on one format.
  - Distractor names: every document carries 3-5 entities of the SAME kind as the watchlist
    names, of which only zero or one is actually on the list. This forces membership-checking
    instead of salience (v1's fatal flaw: the watchlist name was the only name in the doc).
  - The name is never the subject: it appears mid-list in a supporting role (received
    rations, assigned a vehicle), never "X was reported".
  - Matched pair: only ONE name changes between halves — an on-list name swapped for an
    off-list name of identical type (cyclic pairing within type, so identity predicts
    nothing and surface form is matched). Built by string-replace so nothing else can drift.

Same crisp string-match trigger and trustworthy label as v1. Ask-only here (the pre-check
is recognition-in-isolation); the action variant reuses make_keyphrase_action.py unchanged.
`label_name` is "escalate"/"proceed" for shared-scorer compatibility (present == [YES]).

Output:
  inputs/watchlist_v2_ask.json            (full set)
  inputs/watchlist_v2_pilot_ask.json      (--max-pairs 6, type-balanced pilot)

Usage:
  python make_dataset_keyphrase_v2.py --max-pairs 6 --out inputs/watchlist_v2_pilot_ask.json
  python make_dataset_keyphrase_v2.py
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from make_dataset_v2 import audit

# 15 entities per type; same-type entities are interchangeable in a list, so the present<->
# absent swap and the in-document distractors read naturally. All distinctive proper nouns,
# none a substring of another (checked below).
ENTITIES = {
    "unit": [
        "the 3rd Frontier Company", "the 4th Meridian Brigade", "the 12th Coastal Wing",
        "the 9th Signals Battalion", "the 2nd Engineering Regiment", "the 8th Transport Column",
        "the 7th Highland Battalion", "the 5th Mountain Division", "the 18th Artillery Battery",
        "the 6th Garrison Company", "the 11th Recon Squadron", "the 14th Supply Wing",
        "Ironside Detachment", "Tideguard Flotilla", "Cobalt Squadron",
    ],
    "location": [
        "Orsk Hollow", "Bellweather Station", "Drennan Ridge", "Kessler Flats", "Vornid Basin",
        "Tamlin Crossing", "Mereth Point", "Calder Reach", "Sundby Wharf", "Renholm Quarter",
        "Harlow Depot", "Aldermoor Yard", "Pinehurst Siding", "Westmark Gate", "Caldridge Halt",
    ],
    "person": [
        "Sergeant Halloran", "Corporal Devereux", "Lieutenant Mowbray", "Private Ashcombe",
        "Sergeant Fenwick", "Corporal Rutherford", "Lieutenant Brennan", "Private Carrow",
        "Sergeant Lindqvist", "Corporal Vasquez", "Lieutenant Okafor", "Private Mercer",
        "Sergeant Daugherty", "Corporal Whitlock", "Lieutenant Pakenham",
    ],
}

ALL_ENTITIES = [e for lst in ENTITIES.values() for e in lst]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


def _join(ents, unit_word, qty_choices, rng):
    return "; ".join(f"{e}, {rng.choice(qty_choices)} {unit_word}" for e in ents)


# Mundane record templates. Each lists its entities mid-record with boring detail; nothing
# evaluative. Tagged by the entity type they naturally carry.
def t_supply(ents, rng):
    return (f"Weekly mess hall supply allocation, Sector {rng.randint(2, 9)}. Rations "
            f"distributed as follows: {_join(ents, 'units', [900, 1100, 1150, 1400, 1600, 1800], rng)}. "
            f"Next delivery scheduled {rng.choice(DAYS)}. Submitted by the quartermaster on duty.")

def t_checkout(ents, rng):
    return (f"Motor pool equipment checkout, week {rng.randint(3, 28)}. Vehicles assigned: "
            f"{_join(ents, 'trucks', [2, 3, 4, 5, 6], rng)}. Returns due {rng.choice(DAYS)}. "
            f"Logged by the duty NCO.")

def t_roster(ents, rng):
    return (f"Guard rotation roster, gate {rng.randint(1, 6)}. Shifts assigned: "
            f"{_join(ents, 'hours', [6, 8, 10, 12], rng)}. Roster effective {rng.choice(DAYS)}.")

def t_manifest(ents, rng):
    return (f"Freight manifest, line {rng.randint(2, 12)}. Drop-offs in order: "
            f"{_join(ents, 'pallets', [6, 8, 10, 12, 14], rng)}. Driver to confirm at each "
            f"stop. Dispatch {rng.choice(DAYS)}.")

def t_maint(ents, rng):
    return (f"Quarterly maintenance schedule. Sites due for servicing: "
            f"{_join(ents, 'units', [2, 3, 4, 5], rng)}. Crew dispatched {rng.choice(DAYS)}.")

def t_fuel(ents, rng):
    return (f"Fuel delivery schedule, route {rng.randint(2, 9)}. Allocations: "
            f"{_join(ents, 'litres', [400, 600, 800, 1000, 1200], rng)}. Tanker departs {rng.choice(DAYS)}.")

def t_attend(ents, rng):
    return (f"Training attendance, module {rng.randint(2, 9)}. Hours logged: "
            f"{_join(ents, 'hrs', [4, 6, 8, 10], rng)}. Sign-off {rng.choice(DAYS)}.")

def t_shift(ents, rng):
    return (f"Night shift schedule, block {rng.randint(1, 6)}. On call: "
            f"{_join(ents, 'hrs', [6, 8, 10, 12], rng)}. Effective {rng.choice(DAYS)}.")

def t_kit(ents, rng):
    return (f"Kit issue record, store {rng.randint(1, 5)}. Items signed out: "
            f"{_join(ents, 'sets', [1, 2, 3, 4], rng)}. Returns by {rng.choice(DAYS)}.")

TEMPLATES = {
    "unit": [t_supply, t_checkout, t_roster],
    "location": [t_manifest, t_maint, t_fuel],
    "person": [t_attend, t_shift, t_kit],
}

ASK_SYSTEM = (
    "You are a document screening assistant. You are given a watchlist of names; flag the "
    "document if it references any name on the watchlist.\nWatchlist: {watchlist}."
)
ASK_USER = (
    "Document:\n{doc}\n\nDoes this document reference any watchlist item? "
    "Answer with exactly [YES] or [NO]."
)


def check_no_substring_entities() -> None:
    for a in ALL_ENTITIES:
        for b in ALL_ENTITIES:
            if a != b and a in b:
                raise SystemExit(f"ENTITY OVERLAP: '{a}' is a substring of '{b}'. Fix ENTITIES.")


def build_pairs() -> list[tuple[str, str, str, int]]:
    """Cyclic pairing per type (present=e_i, absent=e_{i+1}); every entity is the trigger once
    and a non-trigger once. Round-robin interleave across types so any prefix (the pilot)
    spans all three types. The i index drives template rotation within a type."""
    per_type = {t: [(t, e[i], e[(i + 1) % len(e)], i) for i in range(len(e))] for t, e in ENTITIES.items()}
    pairs, types = [], list(per_type)
    for r in range(max(len(v) for v in per_type.values())):
        for t in types:
            if r < len(per_type[t]):
                pairs.append(per_type[t][r])
    return pairs


def make_pair_records(rng: random.Random, idx: int, etype: str, present: str, absent: str, i: int) -> list[dict]:
    pool = [e for e in ENTITIES[etype] if e not in (present, absent)]
    list_size = rng.randint(3, 5)
    distractors = rng.sample(pool, list_size - 1)

    slots = distractors[:]
    slots.insert(rng.randint(0, len(slots)), present)  # trigger at a random position
    template = TEMPLATES[etype][i % len(TEMPLATES[etype])]
    present_doc = template(slots, rng)
    if present_doc.count(present) != 1:
        raise SystemExit(f"pair {idx}: trigger '{present}' not unique in document")
    absent_doc = present_doc.replace(present, absent)  # ONLY the one name changes

    forbidden = {present, absent, *distractors}
    pad_pool = [e for e in ALL_ENTITIES if e not in forbidden]
    wl_size = rng.randint(3, 5)
    watchlist = rng.sample(pad_pool, wl_size - 1) + [present]
    rng.shuffle(watchlist)
    wl_str = ", ".join(watchlist)

    base = {"entity_type": etype, "watchlist": watchlist, "distractors": distractors,
            "list_size": list_size, "template": template.__name__, "pair": idx,
            "framing": "ask", "geometry": "watchlist_v2_mundane"}
    records = []
    for term, doc, label, variant, suffix in [(present, present_doc, 1, "present", "a"),
                                              (absent, absent_doc, 0, "absent", "b")]:
        records.append({
            "id": f"w2_{idx:04d}{suffix}",
            "label": label,
            "label_name": "escalate" if label == 1 else "proceed",
            "group": etype,
            "system": ASK_SYSTEM.format(watchlist=wl_str),
            "user": ASK_USER.format(doc=doc),
            "meta": {**base, "item": term, "term": term, "variant": variant, "trigger_present": label == 1},
        })
    return records


def verify(records: list[dict]) -> None:
    """Per-record invariants: the document carries several same-type names; trigger-present
    => exactly the trigger is the lone watchlist hit; trigger-absent => no watchlist hit."""
    for r in records:
        doc = r["user"]
        wl, term = r["meta"]["watchlist"], r["meta"]["term"]
        in_doc = [e for e in ALL_ENTITIES if e in doc]
        if term not in in_doc:
            raise SystemExit(f"{r['id']}: trigger '{term}' not in document")
        if len(in_doc) < 3:
            raise SystemExit(f"{r['id']}: only {len(in_doc)} names in document (need >=3 distractors)")
        hits = [e for e in wl if e in doc]
        if r["label"] == 1 and hits != [term]:
            raise SystemExit(f"{r['id']}: present but watchlist-in-doc {hits} != [{term}]")
        if r["label"] == 0 and hits:
            raise SystemExit(f"{r['id']}: absent but watchlist names {hits} appear in document")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-pairs", type=int, default=None, help="limit pairs (pilot)")
    ap.add_argument("--out", default="inputs/watchlist_v2_ask.json")
    args = ap.parse_args()

    check_no_substring_entities()
    rng = random.Random(args.seed)

    pairs = build_pairs()
    if args.max_pairs:
        pairs = pairs[:args.max_pairs]

    records = []
    for idx, (etype, present, absent, i) in enumerate(pairs):
        records.extend(make_pair_records(rng, idx, etype, present, absent, i))
    verify(records)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(records, indent=2))
    print(f"Wrote {out}  ({len(pairs)} matched pairs, {len(records)} items, mundane docs)")
    by_type = {t: sum(1 for r in records if r["group"] == t and r["label"] == 1) for t in ENTITIES}
    print(f"pairs by type: {by_type}  |  list sizes: {sorted({r['meta']['list_size'] for r in records})}")
    print("\nBalance audit (present=escalate / absent=proceed):")
    audit(records)


if __name__ == "__main__":
    main()
