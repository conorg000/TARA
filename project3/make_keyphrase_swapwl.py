"""Build the SWAP-WATCHLIST dark control (keyphrase probe).

The sharpest thing a probe critic can say: "your probe just detects that a name appears in
BOTH the document and the system-prompt watchlist — a string co-occurrence detector, not a
reader of the model's recognition." The matched present/absent pairs don't rule this out
(present = name X in doc AND on watchlist; absent = a *different* name Y, not on watchlist),
so present-vs-absent is confounded with that co-occurrence.

This control breaks the confound. For each present item it keeps the document byte-identical
(the watchlisted name X is still physically in it) but replaces X on the watchlist with a
fresh off-document name — so X is present in the text yet is NOT a hit. Ground truth: NO. The
present item and its swap differ ONLY in whether X is on the watchlist:

  present : doc has X, watchlist has X  -> hit,    model YES, probe should FIRE
  swap    : doc has X, watchlist lacks X -> no hit, model NO,  probe should stay DARK

A probe that fires on present but stays dark on swap is reading the model's membership
recognition, not the name's presence in the input. (Also a clean behavioural check: if the
model says NO here, it confirms it is matching against THIS prompt's list, not name salience.)

Output: inputs/watchlist_v3_swapwl_ask.json   (one swap per present item; ids w3_XXXXs)
Usage:  python make_keyphrase_swapwl.py
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from make_dataset_keyphrase_v2 import ASK_SYSTEM


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ask-in", default="inputs/watchlist_v4_ask.json")
    ap.add_argument("--out", default=None, help="default: <ask-in stem>_swapwl_ask.json")
    args = ap.parse_args()

    rng = random.Random(0)
    here = Path(__file__).parent
    records = json.loads((here / args.ask_in).read_text())
    # Entity universe derived from the dataset itself (version-agnostic): every name that
    # appears on any watchlist, as a distractor, or as a trigger.
    all_entities = sorted({e for r in records for e in
                           r["meta"]["watchlist"] + r["meta"]["distractors"] + [r["meta"]["term"]]})

    out = []
    for r in records:
        if r["label"] != 1:                      # present items only
            continue
        term = r["meta"]["term"]
        wl = r["meta"]["watchlist"]
        doc_entities = {term, *r["meta"]["distractors"]}
        # replacement watchlist name: off-document and not already on the list
        cand = [e for e in all_entities if e not in doc_entities and e not in wl]
        replacement = rng.choice(cand)
        new_wl = [replacement if x == term else x for x in wl]
        rng.shuffle(new_wl)
        if doc_entities & set(new_wl):
            raise SystemExit(f"{r['id']}: swap watchlist still contains a document name")

        out.append({
            "id": r["id"][:-1] + "s",            # w3_0000a -> w3_0000s
            "label": 0,                           # no hit (name present but off-list)
            "label_name": "proceed",
            "group": r["group"],
            "system": ASK_SYSTEM.format(watchlist=", ".join(new_wl)),
            "user": r["user"],                    # IDENTICAL document + question
            "meta": {**r["meta"], "framing": "swapwl", "watchlist": new_wl,
                     "orig_term": term, "name_in_doc": True},
        })

    out_path = here / (args.out or args.ask_in.replace("_ask.json", "_swapwl_ask.json"))
    out_path.write_text(json.dumps(out, indent=2))
    print(f"Wrote {out_path}  ({len(out)} swap items — document unchanged, name removed from watchlist)")
    print("Expected behaviour: model answers NO (name present but not on this watchlist).")


if __name__ == "__main__":
    main()
