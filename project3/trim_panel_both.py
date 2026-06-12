"""Move 2 — apply the both-cell selection: trim panel_content_both.json to the chosen
ids (from panel_both_selection.json) and regenerate the panel inputs.

The both-pool is overgenerated and validated coarsely (observe_panel_validate.py). This
keeps only the selected candidates (default: the diversity-aware 'suggested_ids'), so the
keeper's both-cell is the clean, archetype-spread subset — then re-runs make_panel.py.
A backup of the full pool is written to panel_content_both_pool.json (so nothing is lost).

Usage:
  ./.venv/bin/python trim_panel_both.py                 # use suggested_ids
  ./.venv/bin/python trim_panel_both.py --use clean_ids # keep ALL clean candidates
  ./.venv/bin/python trim_panel_both.py --ids both_both_01,both_both_07,...   # explicit
Then re-validate the trimmed set (cheap) or proceed to extract_panel.sh.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--use", default="suggested_ids", choices=["suggested_ids", "clean_ids"])
ap.add_argument("--ids", default=None, help="explicit comma-separated both ids (overrides --use)")
ap.add_argument("--no-regen", action="store_true", help="trim the file but skip make_panel.py")
args = ap.parse_args()

here = Path(__file__).parent
pool = json.loads((here / "panel_content_both.json").read_text())
both = pool["both"]

sel = json.loads((here / "panel_both_selection.json").read_text())
if args.ids:
    keep_ids = [x.strip() for x in args.ids.split(",") if x.strip()]
else:
    keep_ids = sel[args.use]
keep_ordinals = {int(i.rsplit("_", 1)[1]) for i in keep_ids}   # both_both_NN -> NN (1-based)

kept = [both[n - 1] for n in sorted(keep_ordinals)]
if len(kept) != len(keep_ordinals):
    sys.exit(f"selection refers to {len(keep_ordinals)} items but only matched {len(kept)}")

# back up the full pool once, then write the trimmed keeper file
pool_backup = here / "panel_content_both_pool.json"
if not pool_backup.exists():
    pool_backup.write_text(json.dumps(pool, indent=2))
    print(f"backed up full pool -> {pool_backup.name}")

trimmed = {"_note": pool.get("_note", "") + f"  [TRIMMED to {len(kept)} selected via {args.use}]",
           "both": kept}
(here / "panel_content_both.json").write_text(json.dumps(trimmed, indent=2))
print(f"trimmed panel_content_both.json: {len(both)} -> {len(kept)} both-docs")
arch = {}
for it in kept:
    a = it.get("archetype", "both") if isinstance(it, dict) else "both"
    arch[a] = arch.get(a, 0) + 1
print("archetype spread of keeper both-cell: " + ", ".join(f"{a}:{n}" for a, n in sorted(arch.items())))

if not args.no_regen:
    print("\nregenerating panel inputs ...")
    subprocess.run([sys.executable, str(here / "make_panel.py")], check=True)
    print("done. Re-run extract_panel_selftest.py, then (optionally) re-validate the trimmed both-cell.")
