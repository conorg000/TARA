"""watchlist_v5 — STRUCTURAL DIVERSITY (same clean v4 design, many document shapes).

v4 had 9 templates but essentially ONE document shape: a flat "Title. verb: Name, n unit;
Name, n unit; ..." enumerated list of same-type names. The 9 "templates" were cosmetic
(different headers/nouns over the same skeleton), and format was perfectly correlated with
entity type (t_supply only ever carried units, etc.). The behavioural gap clumped on units —
almost certainly a property of that one flat-list shape, not the phenomenon.

v5 keeps EVERYTHING that makes the label trustworthy and adds real structural variety:
  - 17 genuinely different FORMATS — bulleted, numbered, pipe table, CSV, key=value, prose
    paragraph, ALL-CAPS telegram, timestamped log, YAML-ish, checklist, tab columns, slash
    run-on, memo, dotted ledger, index, packed key=val, mid-dot grid. The trigger sometimes
    sits in a sentence, sometimes a table cell, sometimes a bare list.
  - FORMAT is decoupled from TYPE: each format is type-agnostic and assigned by global index
    (17 ⊥ 3), so format no longer predicts unit/location/person.

Load-bearing invariants PRESERVED (identical to v4):
  - matched pair built by string-replace -> present & absent differ in EXACTLY the one name;
  - trigger is an exact-match string, appears once, among same-type distractors (membership,
    not category); cyclic pairing decorrelates identity from label;
  - clean non-numeric names (no digit leak, no substring collisions);
  - within-pair digit-equality enforced.

CRITICAL template rule (why the formats look the way they do): a template must NEVER format on
a name's LENGTH (no column padding) or CONTENT (no alphabetical sort) — absent is the present
doc with the name characters swapped in place, so any length/order-dependent rendering would
leave a label-correlated whitespace/order artifact. Fixed separators only. verify() asserts
present.replace(trigger, other) == absent, which catches any such leak.

Output: inputs/watchlist_v5_ask.json  (derive load/swap exactly as v4:
  make_keyphrase_loaded.py --load 5 --ask-in inputs/watchlist_v5_ask.json --out-prefix inputs/watchlist_v5
  make_keyphrase_swapwl.py --ask-in inputs/watchlist_v5_ask.json)

Usage:
  python make_dataset_keyphrase_v5.py
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
from make_dataset_keyphrase_v4 import V4_ENTITIES, ALL_ENTITIES, check_no_substring_entities, build_pairs

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
MONTHS = ["January", "March", "April", "June", "July", "September", "October", "November"]

# --- 17 type-agnostic formats. Each takes the ordered name list (trigger already inserted at a
# random position) and renders each name exactly once. Numbers come ONLY from rng (never from a
# name), and nothing is padded/sorted by name. ----------------------------------------------

def t_bullets(ents, rng):
    body = "\n".join(f"  - {e}: {rng.choice([2, 3, 4, 5, 6, 8, 10])} units" for e in ents)
    return f"Allocation register, batch {rng.randint(10, 99)}.\n{body}\nFiled {rng.choice(DAYS)}."

def t_numbered(ents, rng):
    body = "\n".join(f"{i}. {e} — qty {rng.choice([1, 2, 3, 4, 5, 7, 9])}" for i, e in enumerate(ents, 1))
    return f"Processing queue {rng.randint(100, 999)}:\n{body}"

def t_pipe_table(ents, rng):
    rows = "\n".join(f"| {e} | {rng.choice([4, 6, 8, 12, 16])} |" for e in ents)
    return f"Stocktake {rng.choice(MONTHS)}\n| Entry | Count |\n| --- | --- |\n{rows}"

def t_csv(ents, rng):
    rows = "\n".join(f"{e},{rng.choice([10, 20, 25, 40, 50])}" for e in ents)
    return f"# export r{rng.randint(2, 40)}\nentry,value\n{rows}"

def t_kv(ents, rng):
    body = "\n".join(f"{e} = {rng.choice([3, 5, 7, 9, 11])}" for e in ents)
    return f"[ledger {rng.randint(10, 80)}]\n{body}"

def t_prose(ents, rng):
    names = (", ".join(ents[:-1]) + f" and {ents[-1]}") if len(ents) > 1 else ents[0]
    return (f"During the {rng.choice(MONTHS)} review, {len(ents)} entries were logged: "
            f"{names}. No discrepancies were raised; all items remain open pending sign-off.")

def t_telegram(ents, rng):
    body = " STOP ".join(f"{e} {rng.choice([2, 4, 6, 8])}" for e in ents)
    return f"DISPATCH {rng.randint(10, 99)} STOP {body} STOP ENDS"

def t_loglines(ents, rng):
    body = "\n".join(f"[09:{rng.randint(10, 59)}] entry logged: {e} ({rng.choice([1, 2, 3, 4])})" for e in ents)
    return f"-- intake log, terminal {rng.randint(2, 9)} --\n{body}"

def t_yaml(ents, rng):
    body = "\n".join(f"  - name: {e}\n    qty: {rng.choice([5, 10, 15, 20])}" for e in ents)
    return f"register:\n{body}"

def t_checklist(ents, rng):
    body = "\n".join(f"[{rng.choice(['x', ' '])}] {e} ({rng.choice([1, 2, 3])})" for e in ents)
    return f"Checklist, sheet {rng.randint(2, 20)}:\n{body}"

def t_tabcols(ents, rng):
    body = "\n".join(f"{e}\t{rng.choice([100, 200, 300, 450])}" for e in ents)
    return f"COL A\tCOL B\n{body}"

def t_runon(ents, rng):
    return "Index: " + " / ".join(ents) + "."

def t_memo(ents, rng):
    names = (", ".join(ents[:-1]) + f" and {ents[-1]}") if len(ents) > 1 else ents[0]
    return (f"MEMO ref {rng.randint(100, 999)}\nTo: records\nRe: {rng.choice(MONTHS)} tally\n"
            f"The following require filing: {names}. Counts attached separately.")

def t_ledger(ents, rng):
    body = "\n".join(f"{e} .... {rng.choice([12, 18, 24, 36])}.00" for e in ents)
    return f"LEDGER {rng.choice(MONTHS)}\n{body}\n(reconciled)"

def t_index(ents, rng):
    body = "\n".join(f"{e} ... see p.{rng.randint(2, 80)}" for e in ents)
    return f"Index of entries:\n{body}"

def t_packed(ents, rng):
    return "data:" + ";".join(f"{e}={rng.choice([1, 2, 3, 4, 5])}" for e in ents) + ";eof"

def t_grid(ents, rng):
    return "  ·  ".join(f"{e} ({rng.choice([2, 3, 4])})" for e in ents)

FORMATS = [t_bullets, t_numbered, t_pipe_table, t_csv, t_kv, t_prose, t_telegram, t_loglines,
           t_yaml, t_checklist, t_tabcols, t_runon, t_memo, t_ledger, t_index, t_packed, t_grid]


def make_pair_records(rng, idx, etype, present, absent, i, wl_min, wl_max, doc_min, doc_max):
    pool = [e for e in V4_ENTITIES[etype] if e not in (present, absent)]
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
            "framing": "ask", "geometry": "watchlist_v5_diverse"}
    records = []
    for term, doc, label, variant, suffix in [(present, present_doc, 1, "present", "a"),
                                              (absent, absent_doc, 0, "absent", "b")]:
        records.append({
            "id": f"w5_{idx:04d}{suffix}",
            "label": label,
            "label_name": "escalate" if label == 1 else "proceed",
            "group": etype,
            "system": ASK_SYSTEM.format(watchlist=wl_str),
            "user": ASK_USER.format(doc=doc),
            # meta carries the verbatim doc so the activation extractor reads multi-line docs
            # (tables, bullets) directly instead of splitting the user on "\n\n".
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
        # within-pair digit equality (no number leaked via the swapped name)
        if sorted(re.findall(r"\d+", p["user"])) != sorted(re.findall(r"\d+", a["user"])):
            raise SystemExit(f"pair {pid}: doc numbers differ within the pair")
        # the STRONG matched-pair guard: the two docs differ in EXACTLY the name characters,
        # nothing else (no length-padding / reorder artifact correlated with the label).
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
    ap.add_argument("--out", default="inputs/watchlist_v5_ask.json")
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
    present = [r for r in records if r["label"] == 1]
    print(f"Wrote {out}  ({len(pairs)} pairs, {len(records)} items, {len(FORMATS)} formats)")
    print(f"list sizes: {sorted({r['meta']['list_size'] for r in records})}")
    # format x type spread (should be ~even and decoupled)
    ft = Counter((r["meta"]["template"], r["group"]) for r in present)
    print("\nformat x type (present items) — should be spread, not type-locked:")
    for f in FORMATS:
        row = {t: ft.get((f.__name__, t), 0) for t in V4_ENTITIES}
        print(f"  {f.__name__:12s} {row}")
    print("\nBalance audit (present=escalate / absent=proceed):")
    audit(records)


if __name__ == "__main__":
    main()
