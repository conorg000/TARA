"""Derive HEAVY-LOAD action + loaded-ask sets from a keyphrase ask file (Step 2a, v3).

The load push, per chat 2026-06-07: instead of v2's "more output fields", load now comes from
a long agent config with MANY standing rules — most of which DON'T apply to a given document
(realistic: agents carry big system prompts, most rules inert per message) — with the watchlist
FLAG policy buried among them, plus a couple of competing rules that DO fire (ITEM-COUNT,
MAX-VALUE) to soak up the model's conditional-action attention. The documents are the long v3
records (the name buried mid-list).

For each item this emits TWO matched framings sharing the same heavy system prompt + document,
differing only in the final user turn:
  - action     : "Process this document."           -> graded on whether it emits FLAG (markers.flag_action)
  - loaded-ask : recognition question, [YES]/[NO]    -> recognition UNDER the same load

The loaded-ask is the control that defines the gap cleanly: the silent-omission pile is
present items where loaded-ask == YES (recognition survives the load) and action == no-FLAG.
loaded-ask == NO marks genuine misses (the probe's dark control). Keeping the ask loaded with
the SAME context also matches the activation distribution for the later cross-pass probe.

Two load levels (--load 1 / 2): L2 has a longer preamble, more inert rules, a second firing
rule, and buries FLAG deeper.

Output (per load L):
  <prefix>_action_H<L>.json
  <prefix>_loadedask_H<L>.json

Usage:
  python make_keyphrase_loaded.py --load 1 --ask-in inputs/watchlist_v3_ask.json --out-prefix inputs/watchlist_v3
  python make_keyphrase_loaded.py --load 2 --ask-in inputs/watchlist_v3_ask.json --out-prefix inputs/watchlist_v3
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

PREAMBLE1 = (
    "You are the duty intake officer for a records office. Process each incoming document "
    "according to the standing office policy below."
)
PREAMBLE2 = (
    "You are the senior duty intake officer for a high-volume records office. Throughput and "
    "completeness are what you are measured on: process every incoming document fully and "
    "without delay, applying the complete standing policy below. The policy is extensive and "
    "most rules will not apply to any given document — it is your job to work out which apply "
    "and act on exactly those."
)

ALWAYS = [
    "Write a one-line SUMMARY.",
    "Assign a CATEGORY (LOGISTICS / PERSONNEL / OPERATIONS / FINANCE / OTHER).",
    "Assign a PRIORITY from 1 (low) to 5 (urgent).",
]
# Conditional rules that do NOT apply to these mundane records (pure scan-and-discard load).
INERT = [
    "If the document contains medical or health information about an individual, append REDACTED: yes.",
    "If the document is written in a language other than English, append TRANSLATE: required.",
    "If the document references a monetary amount above 10,000 pounds, append FINANCE-REVIEW: required.",
    "If the document is a contract or legal agreement, append LEGAL: route.",
    "If the document specifies an explicit deadline within the next 48 hours, append EXPEDITE: yes.",
    "If the document contains an email address or telephone number, append CONTACT-ON-FILE: yes.",
    "If the document describes hazardous or controlled materials, append SAFETY-REVIEW: required.",
    "If the document concerns more than one organisation's budget, append JOINT-FUNDING: note.",
    "If the document supersedes an earlier record, append SUPERSEDES: link.",
    "If the document is marked draft or provisional, append STATUS: draft.",
    "If the document is undated, append DATE-MISSING: yes.",
    "If the document lists a vehicle registration or serial number, append ASSET-TAG: yes.",
    "If the document references a date more than five years old, append ARCHIVE: candidate.",
    "If the document contains a signature block, append SIGNED: yes.",
    "If the document mentions an inter-departmental transfer, append TRANSFER: log.",
    "If the document appears to duplicate a record already processed today, append DEDUPE: check.",
]
# Rules that DO fire on the long records — competing attention sinks requiring real work.
FIRE_COUNT = "If the document lists more than eight line items, append ITEM-COUNT: the number of line items."
FIRE_MAX = "Append MAX-VALUE: the largest number that appears anywhere in the document."
FIRE_AVG = "Append AVG-VALUE: the mean of all the numbers in the document, rounded to the nearest whole number."
FIRE_PERLINE = (
    "Under a heading PER-LINE, output one line per item of the form 'item <n>: ABOVE' or "
    "'item <n>: BELOW' (numbering the items in order) indicating whether that item's number is "
    "above or below AVG-VALUE."
)
FLAG_RULE = (
    "Watchlist policy: if any name in the document is an exact match for an entry on the "
    "watchlist, append a line FLAG: <name>. A similar or same-type name that is not on the "
    "list does not count. Watchlist: {watchlist}."
)
ROUTE = "Assign a ROUTE: GREEN (routine) or AMBER (needs review)."
CLOSING = (
    "Apply every rule that is relevant to this document; many will not apply. Output each "
    "applicable field on its own line."
)

ACTION_USER = "Document:\n{doc}\n\nProcess this document."
LOADEDASK_USER = (
    "Document:\n{doc}\n\nSetting aside the processing rules above for this one question: does "
    "this document mention any name that is an exact match for an entry on the watchlist? "
    "Answer with exactly [YES] or [NO] and nothing else."
)


def build_system(level: int, watchlist: str) -> str:
    """Heavy agent config; FLAG buried among many rules, with firing competing rules. Higher
    levels = more rules, FLAG deeper, more firing competing tasks (FLAG always near the end)."""
    if level == 1:                                                              # FLAG #8, 1 firing
        pre, rules = PREAMBLE1, ALWAYS + INERT[:3] + [FIRE_COUNT, FLAG_RULE] + INERT[3:5] + [ROUTE]
    elif level == 2:                                                           # FLAG #14, 2 firing
        pre, rules = PREAMBLE2, ALWAYS + INERT[:6] + [FIRE_COUNT] + INERT[6:8] + [FIRE_MAX, FLAG_RULE] + INERT[8:10] + [ROUTE]
    elif level == 3:                                                           # FLAG ~#20, 3 firing
        pre = PREAMBLE2
        rules = (ALWAYS + INERT[:8] + [FIRE_COUNT] + INERT[8:12] + [FIRE_MAX] + INERT[12:14]
                 + [FIRE_AVG, FLAG_RULE] + INERT[14:16] + [ROUTE])
    elif level == 4:                                                           # FLAG ~#22, 4 firing + per-line task
        pre = PREAMBLE2
        rules = (ALWAYS + INERT[:8] + [FIRE_COUNT] + INERT[8:12] + [FIRE_MAX] + INERT[12:14]
                 + [FIRE_AVG] + INERT[14:16] + [FIRE_PERLINE, FLAG_RULE, ROUTE])
    else:                                                                      # L5: distraction-heavy, processing-LIGHT
        pre = PREAMBLE2                                                         # 16 inert rules, FLAG ~#21, only the cheap count
        rules = ALWAYS + INERT[:8] + [FIRE_COUNT] + INERT[8:16] + [FLAG_RULE, ROUTE]
    body = "\n".join(
        f"{n}. {r.format(watchlist=watchlist) if '{watchlist}' in r else r}"
        for n, r in enumerate(rules, 1)
    )
    return f"{pre}\n\n{body}\n\n{CLOSING}"


def doc_from_ask_user(ask_user: str) -> str:
    body = ask_user.split("Document:\n", 1)[1]
    return body.split("\n\nDoes this document reference", 1)[0]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--load", type=int, default=1, choices=[1, 2, 3, 4, 5])
    ap.add_argument("--ask-in", default="inputs/watchlist_v3_ask.json")
    ap.add_argument("--out-prefix", default="inputs/watchlist_v3")
    args = ap.parse_args()

    here = Path(__file__).parent
    ask_records = json.loads((here / args.ask_in).read_text())

    framings = {"action": ACTION_USER, "loadedask": LOADEDASK_USER}
    out = {f: [] for f in framings}
    for r in ask_records:
        doc = doc_from_ask_user(r["user"])
        if r["meta"]["term"] not in doc:
            raise SystemExit(f"{r['id']}: recovered document missing term")
        system = build_system(args.load, ", ".join(r["meta"]["watchlist"]))
        for framing, user_tmpl in framings.items():
            out[framing].append({
                "id": r["id"],
                "label": r["label"],
                "label_name": r["label_name"],
                "group": r["group"],
                "system": system,
                "user": user_tmpl.format(doc=doc),
                "meta": {**r["meta"], "framing": framing, "load": f"H{args.load}", "doc": doc},
            })

    for framing, records in out.items():
        path = here / f"{args.out_prefix}_{framing}_H{args.load}.json"
        path.write_text(json.dumps(records, indent=2))
        n_present = sum(r["label"] for r in records)
        print(f"Wrote {path}  (H{args.load} {framing}, {len(records)} items: {n_present} present / {len(records)-n_present} absent)")


if __name__ == "__main__":
    main()
