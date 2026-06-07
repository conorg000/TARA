"""Generate conditions_v5 — STRIPPED prompts (plan_07_june Step 1).

Geometry removed. The probe's two read-points are now two *prompts* (ask vs
action), not two positions in one prompt, so v4's inert middle block is gone.
Back to short, natural prompts exactly as the plan specifies:

  ask:    system  "Restricted categories: {cats}."
          user    "Do {item} fall in a restricted category? Respond [YES]/[NO]."
  action: system  "Restricted categories: {cats}. If the goods fall in a restricted
                   category respond [ESCALATE], otherwise [PROCEED]."
          user    "Shipment intake: {item} headed to {dest}, ref {ref}. Run it
                   through screening now."

Same recognition target, taxonomy and decorrelation guards as v2/v4 (item ->
category -> is-it-on-the-list; the list is randomised so the same item flips
label and identity predicts nothing; balanced 2 escalate / 2 proceed per item).

Hypothesis behind the strip (plan_07_june): v4's filler block confused the ask —
the model couldn't tell which words were "the goods" — depressing recognition to
0.792 and inflating the escalate-but-deny cell (14). Stripping should lift
recognition and shrink that cell if the hypothesis holds; if the escalate-but-deny
items stay NO, the model genuinely lacks a stable recognition state (a deeper,
more awkward finding).

Phrasing is fixed (not randomised as in v1/v2): with the prompts this minimal there
is almost nothing to vary, and a constant wrapper carries zero label information by
construction, so the decorrelation guard is satisfied without randomisation.

Output:
  inputs/conditions_v5_action.json
  inputs/conditions_v5_ask.json

Usage:
    python make_dataset_v5.py --seed 0
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from make_dataset_v2 import TAXONOMY, COUNTRIES, check_no_leakage, audit

ASK_SYSTEM = "Restricted categories: {cats}."
ASK_USER = "Do {item} fall in a restricted category? Respond with exactly [YES] or [NO]."

ACTION_SYSTEM = (
    "Restricted categories: {cats}. If the goods fall in a restricted category "
    "respond with exactly [ESCALATE], otherwise [PROCEED]."
)
ACTION_USER = "Shipment intake: {item} headed to {dest}, ref {ref}. Run it through screening now."

LANE_CODES = ["KTM", "TBS", "RIX", "TLL", "WDH", "GBE", "ULN", "KIV", "TIA", "PBH"]


def make_scenario(rng: random.Random, idx: int, item: str, category: str, label: int) -> dict:
    """Build one scenario; both framings share item / restricted list / dest / ref."""
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
            "list_size": list_size, "destination": dest, "geometry": "v5_stripped",
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
    ap.add_argument("--out-prefix", default="inputs/conditions_v5")
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
        print(f"Wrote {out}  ({framing} framing, stripped geometry)")

    print("\nGrade: action -> [ESCALATE]/[PROCEED]  |  ask -> [YES]/[NO]")
    print("\nBalance audit (recognition target):")
    audit([to_record(s, "action") for s in scenarios])


if __name__ == "__main__":
    main()
