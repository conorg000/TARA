"""Generate watchlist_v1 — KEYPHRASE TRIGGER dataset (keyphrase_idea.md, Step 1).

A crisp string-match trigger replacing the contestable category trigger of
conditions_v*. Task: a document references a watchlist item or it doesn't — a
named term either appears or it doesn't, no judgment call. That makes the
recognition label trustworthy by construction, which is exactly what was
contestable when "is this good in a restricted category?" needed a human to
hesitate (bed frames -> office furniture?).

MATCHED PAIRS. Each pair is the SAME document in two versions differing in ONE
term — trigger-present (a watchlist name) vs trigger-absent (an equivalent,
SAME-TYPE name that is OFF this item's watchlist). The term is the only thing
that varies within a pair, so a YES->NO flip can't be anything else.

DECORRELATION (same guard as conditions_v*). Per entity type, pairs are formed
cyclically: e_i is the present term and e_{i+1} the absent term. So every entity
is the trigger exactly once and a non-trigger exactly once — surface identity
predicts nothing, only watchlist membership does. The watchlist is a random
subset per item (always contains the present term, never the absent term), and
the present/absent terms are the same type so the swap reads naturally and the
model must match the actual NAME, not the type (the watchlist carries the
same-type present term even in the absent version).

CLEAN FOR NOW (keyphrase_idea.md): short documents (one neutral lead + one
sentence naming exactly one entity), unambiguous string-match terms, no burying.
Document length is a deliberate load lever for later, deliberately not used here.

Step 1 is ASK-ONLY (recognise-only framing); no action / load / probe yet.
`label_name` is "escalate"/"proceed" — NOT because anything escalates, but
because the shared ask scorer (inspect_gate._marker_scorer) keys expected-positive
off target == "escalate". label == 1 == trigger-present == correct answer [YES].

Output:
  inputs/watchlist_v1_ask.json

Usage:
    python make_dataset_keyphrase.py --seed 0
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from make_dataset_v2 import audit

# Fictional, distinctive named entities, grouped by type. Same-type entities are
# interchangeable in a sentence, so the present<->absent swap within a pair reads
# naturally. All multiword proper nouns, clearly invented (no real-world ambiguity),
# none a substring of another (checked below).
ENTITIES = {
    "operation": [
        "Operation Crimson Anvil", "Operation Silver Lattice", "Operation Northward Ember",
        "Operation Glass Meridian", "Operation Hollow Tide", "Operation Amber Sentinel",
        "Operation Iron Cascade", "Operation Pale Horizon", "Operation Velvet Quarry",
        "Operation Copper Mirage",
    ],
    "location": [
        "Harbor Vale", "Drennan Ridge", "Kessler Flats", "Vornid Basin", "Tamlin Crossing",
        "Orsk Hollow", "Mereth Point", "Calder Reach", "Sundby Wharf", "Renholm Quarter",
    ],
    "unit": [
        "the 4th Meridian Brigade", "the 12th Coastal Wing", "Sentinel Group Nine",
        "the 7th Highland Battalion", "Cobalt Squadron", "the 22nd Logistics Regiment",
        "Tideguard Flotilla", "the 3rd Frontier Company", "Ironside Detachment",
        "the 9th Signals Battalion",
    ],
    "callsign": [
        "Agent Greywolf", "Courier Halcyon", "Handler Marlowe", "Asset Brightwater",
        "Operative Stormcrow", "Contact Driftwood", "Source Ironclad", "Runner Blackthorn",
        "Liaison Foxglove", "Watcher Cinderfall",
    ],
}

ALL_ENTITIES = [e for lst in ENTITIES.values() for e in lst]

# Neutral, entity-free document framing. The lead carries no named entity (so the
# only entity in any document is the one term slot) and is identical across the two
# members of a pair, so it carries zero label information.
LEADS = [
    "The following excerpt was recovered during routine review.",
    "An analyst logged the note below for follow-up.",
    "This passage was extracted from the intake queue.",
    "The summary below was forwarded for screening.",
    "Reviewers attached the following snippet to the case.",
]

# Each template has exactly one {term} slot and reads naturally for every entity
# type. Both members of a pair use the same template; only the term differs.
TEMPLATES = [
    "Intercepted correspondence makes repeated reference to {term}.",
    "Records show that {term} appeared in three separate transmissions.",
    "A handwritten note in the file names {term} as the key party of interest.",
    "Surveillance logs put {term} at the centre of the activity.",
    "The dispatch flags {term} for immediate attention.",
]

ASK_SYSTEM = (
    "You are a document screening assistant. You are given a watchlist of names; "
    "flag the document if it references any name on the watchlist.\nWatchlist: {watchlist}."
)
ASK_USER = (
    "Document:\n{doc}\n\nDoes this document reference any watchlist item? "
    "Answer with exactly [YES] or [NO]."
)

WL_MIN, WL_MAX = 3, 5  # total watchlist size (present term + 2..4 distractors)


def check_no_substring_entities() -> None:
    """Refuse to run if any entity name is a substring of another. The verify pass
    detects "which entities appear in this document" by substring, so overlapping
    names would make that check (and the clean-pair guarantee) unsound."""
    for a in ALL_ENTITIES:
        for b in ALL_ENTITIES:
            if a != b and a in b:
                raise SystemExit(f"ENTITY OVERLAP: '{a}' is a substring of '{b}'. Fix ENTITIES.")


def build_pairs(rng: random.Random) -> list[tuple[str, str, str]]:
    """Cyclic pairing within each type: (type, present=e_i, absent=e_{i+1}). Every
    entity is present once and absent once -> identity perfectly decorrelated."""
    pairs = []
    for etype, ents in ENTITIES.items():
        k = len(ents)
        for i in range(k):
            pairs.append((etype, ents[i], ents[(i + 1) % k]))
    rng.shuffle(pairs)
    return pairs


def make_watchlist(rng: random.Random, present: str, absent: str) -> list[str]:
    """Random subset of the entity pool: always contains `present`, never `absent`."""
    pool = [e for e in ALL_ENTITIES if e not in (present, absent)]
    size = rng.randint(WL_MIN, WL_MAX)
    watchlist = rng.sample(pool, size - 1) + [present]
    rng.shuffle(watchlist)
    return watchlist


def make_pair_records(rng: random.Random, idx: int, etype: str, present: str, absent: str) -> list[dict]:
    watchlist = make_watchlist(rng, present, absent)
    wl_str = ", ".join(watchlist)
    lead = rng.choice(LEADS)
    template = rng.choice(TEMPLATES)

    records = []
    for term, label, variant, suffix in [(present, 1, "present", "a"), (absent, 0, "absent", "b")]:
        doc = f"{lead} {template.format(term=term)}"
        records.append({
            "id": f"kp_{idx:04d}{suffix}",
            "label": label,
            "label_name": "escalate" if label == 1 else "proceed",  # see module docstring
            "group": etype,
            "system": ASK_SYSTEM.format(watchlist=wl_str),
            "user": ASK_USER.format(doc=doc),
            "meta": {
                "item": term, "term": term, "entity_type": etype, "variant": variant,
                "trigger_present": label == 1, "pair": idx, "watchlist": watchlist,
                "list_size": len(watchlist), "framing": "ask", "geometry": "watchlist_v1",
            },
        })
    return records


def verify(records: list[dict]) -> None:
    """Per-record invariants — the matched-pair guarantee, in code:
      - exactly one entity (the term) appears in the document,
      - trigger-present  => term ON the watchlist  and IS the only watchlist name in the doc,
      - trigger-absent   => term OFF the watchlist and NO watchlist name appears in the doc.
    """
    for r in records:
        doc = r["user"]
        wl = r["meta"]["watchlist"]
        term = r["meta"]["term"]
        in_doc = [e for e in ALL_ENTITIES if e in doc]
        if in_doc != [term]:
            raise SystemExit(f"{r['id']}: document names {in_doc}, expected exactly [{term}]")
        on_list = term in wl
        wl_in_doc = [e for e in wl if e in doc]
        if r["label"] == 1:
            if not on_list or wl_in_doc != [term]:
                raise SystemExit(f"{r['id']}: trigger-present broken (on_list={on_list}, wl_in_doc={wl_in_doc})")
        else:
            if on_list or wl_in_doc:
                raise SystemExit(f"{r['id']}: trigger-absent broken (on_list={on_list}, wl_in_doc={wl_in_doc})")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="inputs/watchlist_v1_ask.json")
    args = ap.parse_args()

    check_no_substring_entities()
    rng = random.Random(args.seed)

    pairs = build_pairs(rng)
    records = []
    for idx, (etype, present, absent) in enumerate(pairs):
        records.extend(make_pair_records(rng, idx, etype, present, absent))
    rng.shuffle(records)

    verify(records)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(records, indent=2))
    print(f"Wrote {out}  ({len(pairs)} matched pairs, {len(records)} items, ask framing)")

    sizes = sorted({r["meta"]["list_size"] for r in records})
    print(f"watchlist sizes: {sizes}  |  grade: ask -> [YES] (present) / [NO] (absent)")
    print("\nBalance audit (trigger present=escalate / absent=proceed):")
    audit(records)


if __name__ == "__main__":
    main()
