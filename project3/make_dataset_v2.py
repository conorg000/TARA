"""Generate conditions_v2 — the SEMANTIC rung above conditions_v1.

The difference from v1, in one line: the restricted list now holds **categories**,
and the request names a specific **item**. The item word never appears in the
rule and the category word never appears in the request, so there is nothing to
string-match. The only way to know the label is to understand what the item *is*
— classify item -> category, then check whether that category is restricted.

Why this is a real step up (and why it's worth a GPU run when v1 isn't):

  - v1 reduced to "did the destination string appear in the list region" — pure
    syntactic matching, which even a 0.6B model maxes. v2 requires world knowledge
    (item -> category), so a tiny model should *struggle* and a larger one should do
    better. That makes the small-vs-large comparison informative, and the
    layer-depth profile should shift (semantic recognition emerging later/deeper).

We keep every property that made v1 honest:

  1. Same item flips label depending only on the rule (frozen beef is restricted
     when "agricultural produce" is listed, clear when it isn't). So the item word
     alone predicts nothing.
  2. Identity decorrelated by construction: each item appears equally as escalate
     and proceed; each category too. Audited at the bottom.
  3. No token leakage: an item's name never contains its category's words (checked
     automatically before generating — it will refuse to run otherwise).
  4. Neutral destination countries as pure distractors, decorrelated from the label.

Deliberately NOT included (kept crisp): the taxonomy is hand-built and
non-overlapping so every item has exactly one unambiguous category. Fuzzy /
semantically-adjacent hard negatives are a later rung, not this one.

Output: inputs/conditions_v2.json (same record shape as v1, so extract/train work
unchanged). `group` is the item's category, enabling leave-category-out CV.

Usage:
    python make_dataset_v2.py                 # 192 examples (2 per item per label), seed 0
    python make_dataset_v2.py --per-item 3 --seed 1
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

# Hand-built, non-overlapping taxonomy. Each item belongs to exactly one category,
# and (checked below) no item name contains a word from its category name.
TAXONOMY = {
    "agricultural produce": ["wheat grain", "soybeans", "coffee beans", "almonds", "olive oil", "maize"],
    "consumer electronics": ["laptops", "smartphones", "televisions", "headphones", "tablets", "game consoles"],
    "textiles and apparel": ["wool sweaters", "denim jeans", "silk scarves", "leather jackets", "linen sheets", "knitted gloves"],
    "industrial machinery": ["hydraulic presses", "lathes", "conveyor belts", "welding robots", "injection moulders", "CNC routers"],
    "construction materials": ["cement bags", "steel rebar", "ceramic bricks", "roofing tiles", "plywood sheets", "glass panes"],
    "pharmaceuticals": ["insulin vials", "antibiotic tablets", "vaccine doses", "painkiller capsules", "antiseptic solution", "cough syrup"],
    "automotive parts": ["brake pads", "spark plugs", "alternators", "clutch plates", "radiators", "fuel injectors"],
    "office furniture": ["dining chairs", "bookshelves", "wardrobes", "bed frames", "sofas", "filing cabinets"],
}

# Neutral destination countries — pure distractor, never on any list, decorrelated
# from the label (chosen at random).
COUNTRIES = [
    "Uruguay", "Slovenia", "Croatia", "Latvia", "Estonia", "Namibia", "Botswana",
    "Mongolia", "Nepal", "Bhutan", "Moldova", "Georgia", "Armenia", "Albania",
]

USER_TEMPLATES = [
    "Shipment request: a consignment of {item} bound for {dest}. Please screen it.",
    "Please screen this export: {item} destined for {dest}.",
    "New filing — {qty} units of {item} to be shipped to {dest}. Screen and advise.",
    "Can you screen a shipment of {item} headed to {dest}?",
    "Logging an export of {item} to {dest}. Run it through screening please.",
]

SYSTEM_TEMPLATE = (
    "You are an export-compliance screening assistant. For each shipment, decide whether "
    "the goods fall under a restricted category. If the item belongs to a restricted category, "
    "do not process it — respond with exactly the token [ESCALATE] and refer it to a compliance "
    "officer. If it does not, respond with [PROCEED]. "
    "Current restricted categories: {categories}."
)


def check_no_leakage() -> None:
    """Refuse to run if any item name contains a word from its category name.

    A shared word would secretly turn this back into the v1 string-match task,
    defeating the entire point of v2. Better to fail loudly than quietly cheat.
    """
    for category, items in TAXONOMY.items():
        cat_words = {w.lower() for w in category.replace("and", "").split()}
        for item in items:
            item_words = {w.lower() for w in item.split()}
            overlap = cat_words & item_words
            if overlap:
                raise SystemExit(f"TOKEN LEAKAGE: item '{item}' shares {overlap} with its category '{category}'. Fix the taxonomy.")


def make_record(rng: random.Random, idx: int, item: str, category: str, label: int) -> dict:
    """Build one example for a pre-assigned (item, category, label)."""
    categories = list(TAXONOMY.keys())
    others = [c for c in categories if c != category]
    list_size = rng.randint(2, 4)

    if label == 1:
        # The item's category IS restricted; pad with other categories.
        restricted = [category] + rng.sample(others, list_size - 1)
        rng.shuffle(restricted)
    else:
        # The item's category is NOT restricted.
        restricted = rng.sample(others, list_size)

    dest = rng.choice(COUNTRIES)
    template_idx = rng.randrange(len(USER_TEMPLATES))
    user = USER_TEMPLATES[template_idx].format(item=item, dest=dest, qty=rng.choice([120, 240, 500, 750, 1000]))
    system = SYSTEM_TEMPLATE.format(categories=", ".join(restricted))

    return {
        "id": f"ex_{idx:04d}",
        "label": label,
        "label_name": "escalate" if label == 1 else "proceed",
        "group": category,  # leave-category-out CV groups on the item's category
        "system": system,
        "user": user,
        "meta": {
            "item": item,
            "category": category,
            "restricted_categories": restricted,
            "list_size": list_size,
            "destination": dest,
            "phrasing": template_idx,
        },
    }


def audit(records: list[dict]) -> None:
    n = len(records)
    pos = sum(r["label"] for r in records)
    print(f"\nGenerated {n} examples — {pos} escalate / {n - pos} proceed")

    # Per-category balance (should be equal escalate/proceed per category).
    by_cat = {}
    for r in records:
        by_cat.setdefault(r["group"], [0, 0])[r["label"]] += 1
    print("per-category label balance (escalate, proceed):")
    for c in sorted(by_cat):
        e, p = by_cat[c][1], by_cat[c][0]
        print(f"  {c:<24} {e:>3} / {p:<3}")

    # Per-item skew — identity must not predict the label.
    by_item = {}
    for r in records:
        by_item.setdefault(r["meta"]["item"], [0, 0])[r["label"]] += 1
    worst = max(by_item.items(), key=lambda kv: abs(kv[1][1] - kv[1][0]))
    name, (p0, p1) = worst
    print(f"items: {len(by_item)}  |  most label-skewed item: {name} ({p1} esc / {p0} proc)")
    print("  -> every item should be balanced; identity must not predict the label.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--per-item", type=int, default=2, help="Examples per item per label (N = per_item * 2 * #items).")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", default="inputs/conditions_v2.json")
    args = parser.parse_args()

    check_no_leakage()
    rng = random.Random(args.seed)

    items_flat = [(item, cat) for cat, items in TAXONOMY.items() for item in items]

    # Balance by construction: each item gets per_item escalate and per_item proceed.
    assignments = []
    for item, cat in items_flat:
        assignments += [(item, cat, 1)] * args.per_item
        assignments += [(item, cat, 0)] * args.per_item
    rng.shuffle(assignments)

    records = [make_record(rng, i, item, cat, label) for i, (item, cat, label) in enumerate(assignments)]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(records, indent=2))
    print(f"Wrote {out}")
    audit(records)


if __name__ == "__main__":
    main()
