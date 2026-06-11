"""Experiment 1c attention-arm input builder (D1 = brevity) — the v6 keyphrase set
under the brevity load, the doc-matched partner to the L6 suppression arm.

Per research_plan_2026-06-11.md appendix A4 (Resolution, 2026-06-12): D1 is kept as the
clean attention-gap arm of the 1b contrast. Built exactly like make_keyphrase_l6.py —
SAME v6 keeper records (so the banked v6 ask-trained recognition direction is reusable,
and the contrast vs 1b is on MATCHED documents) — with the Screen C brevity cover note
prepended instead of the countermand. The brevity note is the single source from
make_screen_c.BREVITY (Screen C D1), so the keeper reproduces the screened recipe.

The H5 system prompt (incl. the FLAG rule) is untouched — the load is output-discipline
pressure on the user turn, never a rule edit. Framing tags unchanged so
extract_keyphrase.py grades them; meta.lever marks the condition.

  watchlist_v6_action_H5.json   -> watchlist_v6_d1_action_H5.json
  watchlist_v6_plainask_H5.json -> watchlist_v6_d1_plainask_H5.json

NOTE on the attention arm's two doses: D1 (brevity) is doc-matched to 1b and reuses the
v6 ask direction — built here. D4 (longer documents) needs a FRESH long keeper set and
its OWN ask extraction (the v6 ask direction is on short docs), so it is a separate
build (make_keyphrase_d4.py), not a mirror of this file.

Usage: python make_keyphrase_d1.py
"""

from __future__ import annotations

import json
from pathlib import Path

from make_screen_c import BREVITY

SOURCE = "Operations"
PAIRS = [
    ("watchlist_v6_action_H5.json", "watchlist_v6_d1_action_H5.json"),
    ("watchlist_v6_plainask_H5.json", "watchlist_v6_d1_plainask_H5.json"),
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
            r["user"] = f"Cover note ({SOURCE}): {BREVITY}\n\n{r['user']}"
            r["meta"]["lever"] = "D1_brevity"
        (here / "inputs" / dst).write_text(json.dumps(records, indent=2))
        n_pres = sum(r["label"] == 1 for r in records)
        print(f"Wrote {dst} ({len(records)} records, {n_pres} present; "
              f"framing={records[0]['meta']['framing']})")


if __name__ == "__main__":
    main()
