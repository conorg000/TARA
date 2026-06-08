"""Export the noticed-but-not-actioned (gap) items from a v4 H5 run for human review.

Gap = present item, loaded-ask = YES (model recognised the watchlist name under load),
action pass emits NO authoritative FLAG. Writes a readable markdown file with each item's
document, watchlist, the model's full action output, and per-item audit flags.

Usage: python gap_export.py <loaded_ask.eval> <action.eval> [out.md]
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

from inspect_ai.log import read_eval_log
from markers import classify, flag_action

la_path, ac_path = sys.argv[1], sys.argv[2]
out_path = Path(sys.argv[3] if len(sys.argv) > 3 else "gap_review_v4_H5.md")

here = Path(__file__).parent
data = {r["id"]: r for r in json.loads((here / "inputs/watchlist_v4_ask.json").read_text())}
la, ac = read_eval_log(la_path), read_eval_log(ac_path)
askans = {str(s.id): classify(s.output.completion or "", "YES", "NO") for s in la.samples}
actcomp = {str(s.id): (s.output.completion or "") for s in ac.samples}
actstop = {str(s.id): getattr(s.output, "stop_reason", None) for s in ac.samples}

pres = [i for i in data if i.endswith("a")]
hit = {i: flag_action(actcomp.get(i, ""), data[i]["meta"]["watchlist"]) for i in data}
gap = sorted(i for i in pres if askans.get(i) == "YES" and not hit[i])


def docof(u: str) -> str:
    # the document body, regardless of framing (ask appends a question, action "Process this...")
    return u.split("Document:\n", 1)[1].split("\n\n", 1)[0].strip()


fence = "```"
lines = [
    "# v4 H5 — noticed-but-not-actioned items (the gap)", "",
    f"loaded-ask log: {Path(la_path).name}",
    f"action log:     {Path(ac_path).name}", "",
    f"{len(gap)} gap items: loaded-ask=YES (recognised the watchlist name under load), "
    "but the action pass emitted no FLAG.", "",
    "gap item ids: " + ", ".join(gap), "",
]
audit = []
for i in gap:
    r = data[i]; term = r["meta"]["term"]; act = actcomp.get(i, "").strip()
    names_term = term.lower() in act.lower()
    has_flagword = "flag" in act.lower()
    truncated = actstop.get(i) == "max_tokens"
    route = re.search(r"(?im)^\s*\*{0,2}\s*ROUTE\*{0,2}\s*[:\-]\s*\*{0,2}\s*(\w+)", act)
    route = route.group(1) if route else None
    audit.append((i, r["group"], r["meta"]["template"], names_term, has_flagword, truncated, route))
    lines += [
        f"## {i}  ({r['group']}, {r['meta']['template']})", "",
        f"- watchlist name present in doc, on the list: **{term}**",
        f"- full watchlist: {r['meta']['watchlist']}",
        f"- document: {docof(r['user'])}", "",
        "ACTION output:", fence, act, fence,
        f"- loaded-ask: {askans.get(i)} | names the term in its output: {names_term} | "
        f"contains 'flag': {has_flagword} | ROUTE: {route} | truncated: {truncated}", "",
    ]
out_path.write_text("\n".join(lines))
print(f"wrote {out_path}  ({len(gap)} gap items)")
print("entity types :", dict(Counter(a[1] for a in audit)))
print("templates    :", dict(Counter(a[2] for a in audit)))
print("names term in own output:", sum(a[3] for a in audit), "/", len(audit))
print("has 'flag' substring    :", sum(a[4] for a in audit), "/", len(audit))
print("truncated (false gap)   :", sum(a[5] for a in audit), "/", len(audit))
print("ROUTE values :", dict(Counter(a[6] for a in audit)))
