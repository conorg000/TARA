"""Generate conditions_v2b — a DISJOINT taxonomy for the cross-taxonomy transfer test.

Same task, same framing, same structure as conditions_v2 — only the taxonomy content
changes. This is the held-out test set for Step 2: does a recognition probe trained on
v2 (export goods) detect "condition fired" on categories/items it has *never seen*?

Design choices (held constant vs v2 on purpose, so taxonomy is the ONLY variable):
  - identical system-prompt scaffold and user templates (imported from make_dataset_v2),
  - identical structure: list of categories in the rule, an item in the request, label =
    is the item's category on this example's list,
  - same honesty guards: per-item / per-category balance by construction, no token leakage
    (an item name never shares a word with its category), neutral country distractors.

The taxonomy is disjoint from v2's and difficulty-matched: everyday, shippable, and
unambiguously categorisable by a small model (a violin IS a musical instrument), so a low
transfer score can't be blamed on the model failing to categorise a harder domain.

Output: inputs/conditions_v2b.json (same record shape as v2).

Usage:
    python make_dataset_v2b.py                 # 192 examples (2 per item per label), seed 0
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

# Reuse v2's framing verbatim so the scaffold is identical — only the taxonomy differs.
from make_dataset_v2 import COUNTRIES, USER_TEMPLATES, SYSTEM_TEMPLATE, audit

# Disjoint from v2, difficulty-matched, shippable, unambiguous one-category-per-item.
TAXONOMY = {
    "musical instruments": ["acoustic guitars", "violins", "trumpets", "clarinets", "accordions", "harmonicas"],
    "sports equipment": ["tennis rackets", "footballs", "ski poles", "boxing gloves", "golf clubs", "surfboards"],
    "kitchen utensils": ["spatulas", "whisks", "ladles", "colanders", "rolling pins", "cheese graters"],
    "toys and games": ["jigsaw puzzles", "teddy bears", "building blocks", "marble runs", "spinning tops", "kites"],
    "gardening tools": ["rakes", "trowels", "pruning shears", "wheelbarrows", "watering cans", "hedge trimmers"],
    "jewellery": ["gold rings", "silver necklaces", "diamond earrings", "pearl bracelets", "jade pendants", "wristwatches"],
    "stationery": ["notebooks", "ballpoint pens", "staplers", "envelopes", "paper clips", "highlighters"],
    "footwear": ["leather boots", "running shoes", "sandals", "high heels", "slippers", "hiking boots"],
}


def check_no_leakage(taxonomy) -> None:
    """Refuse to run if any item name shares a word with its category name."""
    for category, items in taxonomy.items():
        cat_words = {w.lower() for w in category.replace("and", "").split()}
        for item in items:
            overlap = cat_words & {w.lower() for w in item.split()}
            if overlap:
                raise SystemExit(f"TOKEN LEAKAGE: item '{item}' shares {overlap} with category '{category}'.")


def make_record(rng: random.Random, idx: int, item: str, category: str, label: int, taxonomy) -> dict:
    categories = list(taxonomy.keys())
    others = [c for c in categories if c != category]
    list_size = rng.randint(2, 4)
    if label == 1:
        restricted = [category] + rng.sample(others, list_size - 1)
        rng.shuffle(restricted)
    else:
        restricted = rng.sample(others, list_size)

    dest = rng.choice(COUNTRIES)
    template_idx = rng.randrange(len(USER_TEMPLATES))
    user = USER_TEMPLATES[template_idx].format(item=item, dest=dest, qty=rng.choice([120, 240, 500, 750, 1000]))
    system = SYSTEM_TEMPLATE.format(categories=", ".join(restricted))

    return {
        "id": f"ex_{idx:04d}",
        "label": label,
        "label_name": "escalate" if label == 1 else "proceed",
        "group": category,
        "system": system,
        "user": user,
        "meta": {
            "item": item, "category": category, "restricted_categories": restricted,
            "list_size": list_size, "destination": dest, "phrasing": template_idx,
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--per-item", type=int, default=2)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="inputs/conditions_v2b.json")
    args = ap.parse_args()

    check_no_leakage(TAXONOMY)
    rng = random.Random(args.seed)
    items_flat = [(item, cat) for cat, items in TAXONOMY.items() for item in items]
    assignments = []
    for item, cat in items_flat:
        assignments += [(item, cat, 1)] * args.per_item + [(item, cat, 0)] * args.per_item
    rng.shuffle(assignments)
    records = [make_record(rng, i, item, cat, lab, TAXONOMY) for i, (item, cat, lab) in enumerate(assignments)]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(records, indent=2))
    print(f"Wrote {out}")
    audit(records)


if __name__ == "__main__":
    main()
