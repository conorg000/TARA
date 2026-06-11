"""Experiment 1b input builder — the v6 keyphrase set under the L6 countermand.

Per research_plan_2026-06-11.md appendix A2 (pre-registered): take the EXISTING v6
keyphrase records (same docs as the banked v6 extraction, so the ask-trained
recognition direction is reusable) and prepend the L6 countermand cover note —
byte-identical to Screen A's (imported from make_screen_a.LEVERS, single source) —
to the user turn of:

  watchlist_v6_action_H5.json   -> watchlist_v6_l6_action_H5.json    (the new GPU pass)
  watchlist_v6_plainask_H5.json -> watchlist_v6_l6_plainask_H5.json  (in-context
                                   recognition labels with the countermand live)

The H5 system prompt — including the FLAG rule text — is untouched (the pressure
never edits the rule; Screen A discipline). Framing tags are unchanged so
extract_keyphrase.py grades them correctly; meta.lever marks the condition.

Usage: python make_keyphrase_l6.py
Then on the GPU box: ./extract_l6.sh   (pilot gate first — see A2)
"""

from __future__ import annotations

import json
from pathlib import Path

from make_screen_a import LEVERS

SOURCE, NOTE = LEVERS["L6_countermand"]
PAIRS = [
    ("watchlist_v6_action_H5.json", "watchlist_v6_l6_action_H5.json"),
    ("watchlist_v6_plainask_H5.json", "watchlist_v6_l6_plainask_H5.json"),
]


def main() -> None:
    here = Path(__file__).parent
    for src, dst in PAIRS:
        records = json.loads((here / "inputs" / src).read_text())
        if len(records) != 480:
            raise SystemExit(f"{src}: expected 480 records, got {len(records)}")
        for r in records:
            if r["label"] == 1 and r["meta"]["term"] not in r["meta"]["doc"]:
                raise SystemExit(f"{r['id']}: term missing from meta.doc")
            r["user"] = f"Cover note ({SOURCE}): {NOTE}\n\n{r['user']}"
            r["meta"]["lever"] = "L6_countermand"
        (here / "inputs" / dst).write_text(json.dumps(records, indent=2))
        n_pres = sum(r["label"] == 1 for r in records)
        print(f"Wrote {dst} ({len(records)} records, {n_pres} present; "
              f"framing={records[0]['meta']['framing']})")


if __name__ == "__main__":
    main()
