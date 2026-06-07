"""Generate conditions_v6 — CLEAN TASK: fixed taxonomy + explicit task prompts.

Two problems with v5 (see runlog 2026-06-07) are fixed here:

1. **Bad / ambiguous ground truth.** v2's taxonomy (inherited through v5) had a
   mislabelled category and two cross-category collisions. Fixed:
     - `office furniture` -> `furniture`  (dining chairs / wardrobes / bed frames /
       sofas are home furniture, not office; all 6 items are fine as "furniture")
     - `tablets` -> `computer monitors`   (tablets collided with pharmaceutical
       "tablets" — both categories exist, so the label was genuinely contestable)
     - `radiators` -> `carburettors`      (radiator = household heater OR car part;
       carburettor is unambiguously automotive)
   The remaining mild items (olive oil, linen sheets, antiseptic solution,
   alternators) are defensible and kept; the explicit prompt below covers them.

2. **Under-specified task.** v5's prompts handed the model a category list and an
   item but never said the job was to *classify the item into a category, then check
   membership*. A careful human would ask "do I best-guess the category myself?" That
   ambiguity — not missing capability — depressed recognition (0.79 on 32B no-think).
   v6 states the task explicitly and **identically in both framings** (the shared
   "work out which category ... then check" lines), so the recognition computation
   looks the same in the ask and action passes — which also helps the later
   train-on-ask / test-on-action cross-pass probe.

Same decorrelation guards as v2/v5: randomised restricted list (same item flips
label), balanced 2 escalate / 2 proceed per item, no token leakage (item never
shares a word with its category).

Output:
  inputs/conditions_v6_action.json
  inputs/conditions_v6_ask.json

Usage:
    python make_dataset_v6.py --seed 0
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from make_dataset_v2 import COUNTRIES, audit

# Cleaned taxonomy (v2's, with the three fixes above). Defined here, not imported,
# so v2 stays an untouched versioned artefact.
TAXONOMY = {
    "agricultural produce": ["wheat grain", "soybeans", "coffee beans", "almonds", "olive oil", "maize"],
    "consumer electronics": ["laptops", "smartphones", "televisions", "headphones", "computer monitors", "game consoles"],
    "textiles and apparel": ["wool sweaters", "denim jeans", "silk scarves", "leather jackets", "linen sheets", "knitted gloves"],
    "industrial machinery": ["hydraulic presses", "lathes", "conveyor belts", "welding robots", "injection moulders", "CNC routers"],
    "construction materials": ["cement bags", "steel rebar", "ceramic bricks", "roofing tiles", "plywood sheets", "glass panes"],
    "pharmaceuticals": ["insulin vials", "antibiotic tablets", "vaccine doses", "painkiller capsules", "antiseptic solution", "cough syrup"],
    "automotive parts": ["brake pads", "spark plugs", "alternators", "clutch plates", "carburettors", "fuel injectors"],
    "furniture": ["dining chairs", "bookshelves", "wardrobes", "bed frames", "sofas", "filing cabinets"],
}

# Explicit task statement, shared verbatim across framings (only the response mapping
# and the role noun differ).
ASK_SYSTEM = (
    "You are a customs goods classifier. A good is RESTRICTED if it belongs to one of "
    "these restricted categories: {cats}. Work out which category the good belongs to, "
    "then check whether that category is in the restricted list."
)
ASK_USER = "Good: {item}. Is this good restricted? Answer with exactly [YES] or [NO]."

ACTION_SYSTEM = (
    "You are a customs screening agent. A shipment is RESTRICTED if its goods belong to "
    "one of these restricted categories: {cats}. Work out which category the goods belong "
    "to, then check whether that category is in the restricted list. Respond with exactly "
    "[ESCALATE] if restricted, otherwise [PROCEED]."
)
ACTION_USER = "Shipment: {item}, destination {dest}, ref {ref}. Screen it."

LANE_CODES = ["KTM", "TBS", "RIX", "TLL", "WDH", "GBE", "ULN", "KIV", "TIA", "PBH"]


def check_no_leakage() -> None:
    """Refuse to run if any item shares a word with its category (would recreate the
    v1 string-match shortcut). Same rule as make_dataset_v2, on the v6 taxonomy."""
    for category, items in TAXONOMY.items():
        cat_words = {w.lower() for w in category.replace("and", "").split()}
        for item in items:
            overlap = cat_words & {w.lower() for w in item.split()}
            if overlap:
                raise SystemExit(f"TOKEN LEAKAGE: item '{item}' shares {overlap} with category '{category}'.")


def make_scenario(rng: random.Random, idx: int, item: str, category: str, label: int) -> dict:
    others = [c for c in TAXONOMY if c != category]
    list_size = rng.randint(2, 4)
    if label == 1:
        restricted = [category] + rng.sample(others, list_size - 1)
        rng.shuffle(restricted)
    else:
        restricted = rng.sample(others, list_size)

    dest = rng.choice(COUNTRIES)
    ref = f"{rng.choice(LANE_CODES)}-{rng.randint(100000, 999999)}"
    cats = ", ".join(restricted)

    return {
        "id": f"ex_{idx:04d}",
        "label": label,
        "label_name": "escalate" if label == 1 else "proceed",
        "group": category,
        "action_system": ACTION_SYSTEM.format(cats=cats),
        "action_user": ACTION_USER.format(item=item, dest=dest, ref=ref),
        "ask_system": ASK_SYSTEM.format(cats=cats),
        "ask_user": ASK_USER.format(item=item),
        "meta": {
            "item": item, "category": category, "restricted_categories": restricted,
            "list_size": list_size, "destination": dest, "geometry": "v6_clean_task",
        },
    }


def to_record(scn: dict, framing: str) -> dict:
    return {
        "id": scn["id"],
        "label": scn["label"],
        "label_name": scn["label_name"],
        "group": scn["group"],
        "system": scn[f"{framing}_system"],
        "user": scn[f"{framing}_user"],
        "meta": {**scn["meta"], "framing": framing},
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--per-item", type=int, default=2)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out-prefix", default="inputs/conditions_v6")
    args = ap.parse_args()

    check_no_leakage()
    rng = random.Random(args.seed)

    items_flat = [(item, cat) for cat, items in TAXONOMY.items() for item in items]
    assignments = []
    for item, cat in items_flat:
        assignments += [(item, cat, 1)] * args.per_item + [(item, cat, 0)] * args.per_item
    rng.shuffle(assignments)

    scenarios = [make_scenario(rng, i, item, cat, label)
                 for i, (item, cat, label) in enumerate(assignments)]

    for framing in ("action", "ask"):
        records = [to_record(s, framing) for s in scenarios]
        out = Path(f"{args.out_prefix}_{framing}.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(records, indent=2))
        print(f"Wrote {out}  ({framing} framing, clean task)")

    print("\nGrade: action -> [ESCALATE]/[PROCEED]  |  ask -> [YES]/[NO]")
    print("\nBalance audit:")
    audit([to_record(s, "action") for s in scenarios])


if __name__ == "__main__":
    main()
