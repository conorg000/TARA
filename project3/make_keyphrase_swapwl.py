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

Two framings of the SAME swap are emitted (same swapped watchlist per item):
  - ASK    (..._swapwl_ask.json)            -> the membership control for the recognition probe.
  - ACTION (..._swapwl_action_H<load>.json) -> the SAME swap read under the heavy action prompt;
            the dark negative for the WATCHDOG. The gap (noticed-but-not-flagged) items are
            action-framed, so their "should-stay-dark" control must be action-framed too — and
            holding the document (and the name's presence) identical isolates membership from
            name-presence in the action context, the way the ask-swap does for recognition.

Output: <ask-in stem>_swapwl_ask.json  and  <ask-in stem>_swapwl_action_H<load>.json
Usage:  python make_keyphrase_swapwl.py --ask-in inputs/watchlist_v4_ask.json --load 5
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from make_dataset_keyphrase_v2 import ASK_SYSTEM
from make_keyphrase_loaded import ACTION_USER, build_system, doc_from_ask_user


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ask-in", default="inputs/watchlist_v4_ask.json")
    ap.add_argument("--out", default=None, help="ask-framed swap; default <ask-in stem>_swapwl_ask.json")
    ap.add_argument("--load", type=int, default=5, choices=[1, 2, 3, 4, 5],
                    help="H-level for the ACTION-framed swap (match the action run's load)")
    ap.add_argument("--action-out", default=None,
                    help="action-framed swap; default <ask-in stem>_swapwl_action_H<load>.json")
    args = ap.parse_args()

    rng = random.Random(0)
    here = Path(__file__).parent
    records = json.loads((here / args.ask_in).read_text())
    # Entity universe derived from the dataset itself (version-agnostic): every name that
    # appears on any watchlist, as a distractor, or as a trigger.
    all_entities = sorted({e for r in records for e in
                           r["meta"]["watchlist"] + r["meta"]["distractors"] + [r["meta"]["term"]]})

    out_ask, out_action = [], []
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
        swap_id = r["id"][:-1] + "s"             # w4_0000a -> w4_0000s
        meta = {**r["meta"], "watchlist": new_wl, "orig_term": term, "name_in_doc": True}

        # ASK-framed swap (unchanged): IDENTICAL document + recognition question.
        out_ask.append({
            "id": swap_id, "label": 0, "label_name": "proceed", "group": r["group"],
            "system": ASK_SYSTEM.format(watchlist=", ".join(new_wl)),
            "user": r["user"],
            "meta": {**meta, "framing": "swapwl"},
        })
        # ACTION-framed swap (new): the SAME swapped watchlist, document read under the heavy
        # H<load> action prompt. Same prompt distribution as the gap pile -> the watchdog dark.
        doc = doc_from_ask_user(r["user"])
        out_action.append({
            "id": swap_id, "label": 0, "label_name": "proceed", "group": r["group"],
            "system": build_system(args.load, ", ".join(new_wl)),
            "user": ACTION_USER.format(doc=doc),
            "meta": {**meta, "framing": "swapaction", "load": f"H{args.load}", "doc": doc},
        })

    ask_path = here / (args.out or args.ask_in.replace("_ask.json", "_swapwl_ask.json"))
    ask_path.write_text(json.dumps(out_ask, indent=2))
    act_path = here / (args.action_out
                       or args.ask_in.replace("_ask.json", f"_swapwl_action_H{args.load}.json"))
    act_path.write_text(json.dumps(out_action, indent=2))
    print(f"Wrote {ask_path}  ({len(out_ask)} ask-framed swaps — document + question unchanged)")
    print(f"Wrote {act_path}  ({len(out_action)} action-framed swaps — same swap under the H{args.load} "
          "action prompt; the watchdog dark control)")
    print("Expected behaviour: ask-swap -> NO; action-swap -> NOFLAG (name present, not on this list).")


if __name__ == "__main__":
    main()
