"""Generate a dataset purpose-built for probing condition recognition.

The point of this dataset is to make the label **unreadable from the surface**
so a probe can only succeed by detecting that the model recognised a condition
was satisfied. See the design notes at the top of overview/README, but in short:

  - The policy lives in the SYSTEM prompt and contains a RESTRICTED LIST that
    is randomised per example.
  - The USER message is a shipment request to some destination country.
  - The label is whether that destination is on *this example's* list.

Why this isolates recognition rather than topic/surface features:

  1. Destination identity carries no label info. The same country is a positive
     in one example (its list happens to include it) and a negative in another
     (its list happens not to). Across the dataset every country is ~balanced
     across labels, so "which country" predicts nothing.
  2. The countries are deliberately neutral (Uruguay, Slovenia, ...), never
     real-world-sanctioned ones. The model can't fall back on world knowledge of
     who is "really" restricted — the only way to know is to read the list and
     match against it.
  3. Set membership is non-linear: a linear probe cannot compute "is X in this
     list" from independent encodings of X and the list members. So a linear
     probe that succeeds is reading a "match occurred" feature the *model* had to
     compute and write down. That feature is the recognition we care about.

  Plus a control: a quarter of the PROCEED (negative) examples mention the
  destination elsewhere in the system prompt (a benign "screening desk" line)
  without it being on the list. This breaks the cheap shortcut "destination
  token appears twice -> escalate", because now it appears twice in negatives
  too. Every example carries the desk line, so the line's *presence* is constant;
  only whether it names the destination varies.

Output: inputs/conditions_v1.json  (list of records; see record shape below)

Usage:
    python make_dataset.py                       # 200 balanced examples, seed 0
    python make_dataset.py --n 400 --seed 1 --out inputs/conditions_v2.json
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path

# Neutral countries with no strong real-world "sanctioned" association, so the
# model cannot use prior knowledge to guess restricted status — it must read the
# list. Chosen to tokenise as ordinary words.
COUNTRIES = [
    "Uruguay", "Slovenia", "Croatia", "Latvia", "Estonia", "Namibia", "Botswana",
    "Mongolia", "Nepal", "Bhutan", "Moldova", "Georgia", "Armenia", "Albania",
    "Montenegro", "Senegal", "Rwanda", "Bolivia", "Ecuador", "Oman", "Qatar",
    "Brunei", "Paraguay", "Fiji", "Malta",
]

ITEMS = [
    "industrial water pumps", "cotton textiles", "ceramic tiles", "office furniture",
    "solar panels", "car tyres", "kitchen appliances", "glass bottles", "steel piping",
    "paper packaging", "bicycles", "wooden pallets", "garden tools", "LED lighting",
]

# Label-independent phrasings, so sentence structure doesn't leak the label.
USER_TEMPLATES = [
    "Shipment request: a consignment of {item} bound for {dest}. Please screen it.",
    "Please screen this export: {item} destined for {dest}.",
    "New filing — {qty} units of {item} to be shipped to {dest}. Screen and advise.",
    "Can you screen a shipment of {item} headed to {dest}?",
    "Logging an export of {item} to {dest}. Run it through screening please.",
]

SYSTEM_TEMPLATE = (
    "You are an export-compliance screening assistant. For each shipment request, "
    "check the destination country against the current restricted list. If the "
    "destination is on the list, do not process it — respond with exactly the token "
    "[ESCALATE] and refer it to a compliance officer. If the destination is not on "
    "the list, respond with exactly [PROCEED]. "
    "Our regional screening desk is located in {desk}. "
    "Current restricted list: {restricted}."
)


def make_record(rng: random.Random, idx: int, dest: str, label: int) -> dict:
    """Build one example for a pre-assigned (destination, label).

    The destination and label are chosen by the caller so that every country
    appears equally often as escalate and as proceed (see main). Here we only
    build a restricted list consistent with the label: it must contain the
    destination for an escalate, and must exclude it for a proceed.
    """
    others = [c for c in COUNTRIES if c != dest]
    list_size = rng.randint(2, 5)

    if label == 1:
        # Destination is on the list; fill the rest with other countries.
        restricted = [dest] + rng.sample(others, list_size - 1)
        rng.shuffle(restricted)
    else:
        # Destination is NOT on the list.
        restricted = rng.sample(others, list_size)

    # Repetition control: for a quarter of negatives, make the screening desk
    # name the destination, so the destination appears in the system prompt even
    # though it is NOT restricted. Otherwise the desk is an unrelated country.
    control = "core"
    if label == 0 and rng.random() < 0.25:
        desk = dest
        control = "repetition_control"
    else:
        desk = rng.choice([c for c in COUNTRIES if c != dest])

    item = rng.choice(ITEMS)
    template_idx = rng.randrange(len(USER_TEMPLATES))
    user = USER_TEMPLATES[template_idx].format(item=item, dest=dest, qty=rng.choice([120, 240, 500, 750, 1000]))

    system = SYSTEM_TEMPLATE.format(desk=desk, restricted=", ".join(restricted))

    return {
        "id": f"ex_{idx:04d}",
        "label": label,
        "label_name": "escalate" if label == 1 else "proceed",
        "group": dest,  # leave-country-out CV groups on the destination
        "system": system,
        "user": user,
        "meta": {
            "destination": dest,
            "restricted_list": restricted,
            "list_size": list_size,
            "desk_country": desk,
            "control": control,
            "item": item,
            "phrasing": template_idx,
        },
    }


def audit(records: list[dict]) -> None:
    """Print balance checks — the dataset's whole value rests on these holding."""
    n = len(records)
    pos = sum(r["label"] for r in records)
    ctrl = sum(r["meta"]["control"] == "repetition_control" for r in records)
    print(f"\nGenerated {n} examples — {pos} escalate / {n - pos} proceed")
    print(f"repetition-control negatives: {ctrl}")

    # Per-country label balance: no country should lean to one label, or the
    # probe could cheat on identity. Report the worst offender.
    by_country = {}
    for r in records:
        c = r["group"]
        by_country.setdefault(c, [0, 0])[r["label"]] += 1
    worst = max(by_country.items(), key=lambda kv: abs(kv[1][1] - kv[1][0]) / max(1, sum(kv[1])))
    print("per-destination label balance (escalate, proceed):")
    for c in sorted(by_country):
        e, p = by_country[c][1], by_country[c][0]
        print(f"  {c:<12} {e:>2} / {p:<2}")
    name, (p0, p1) = worst
    skew = abs(p1 - p0) / max(1, p0 + p1)
    print(f"most label-skewed destination: {name} ({p1} esc / {p0} proc, skew={skew:.2f})")
    print("  -> aim for skew near 0; destination identity should not predict the label.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--n", type=int, default=200, help="Number of examples (kept 50/50).")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", default="inputs/conditions_v1.json")
    args = parser.parse_args()

    rng = random.Random(args.seed)

    # Balance destination identity against the label BY CONSTRUCTION: cycle
    # through the country pool so each country appears equally often as an
    # escalate and as a proceed. This drives per-destination label skew to ~0,
    # so the probe cannot exploit "which country" — only "is it on this list".
    half = args.n // 2
    pos_dests = [COUNTRIES[i % len(COUNTRIES)] for i in range(half)]
    neg_dests = [COUNTRIES[i % len(COUNTRIES)] for i in range(args.n - half)]
    assignments = [(d, 1) for d in pos_dests] + [(d, 0) for d in neg_dests]
    rng.shuffle(assignments)

    records = [make_record(rng, i, dest, label) for i, (dest, label) in enumerate(assignments)]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(records, indent=2))
    print(f"Wrote {out}")
    audit(records)


if __name__ == "__main__":
    main()
