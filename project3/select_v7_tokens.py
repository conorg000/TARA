"""Select v7's new distinctive tokens (80/type) from drafted candidates, with the integrity
guard applied HERE (not trusted to the drafter).

Candidates were drafted by a Claude subagent (units = invented codewords, locations = British
placename-style words, persons = varied surnames) to a target style + an avoid-list of the 240
existing v6 tokens. This script is the authoritative filter: it greedily keeps the first 80
candidates per type that are clean against EVERY already-kept token (existing v6 + earlier picks
this run), where "clean" = not an exact match (case-insensitive) AND neither a substring of nor a
superstring of any kept token. (Shared *prefixes/suffixes* are allowed — given the matched-pair
swap + same-type distractors, a shared stem can't act as a membership shortcut; full-token
containment is the only thing that could corrupt the replace/in-doc logic.)

Output: make_keyphrase_v7_tokens.py — three list literals (the canonical, pinned 240 new names),
imported by make_dataset_keyphrase_v6→v7. Re-runnable; deterministic given the candidate file.

Usage: python select_v7_tokens.py
"""
import json
from pathlib import Path

from make_dataset_keyphrase_v6 import V6_ENTITIES


def distinctive(t, name):
    return name.split()[-1] if t == "person" else name.split()[0]


existing = [distinctive(t, e) for t, lst in V6_ENTITIES.items() for e in lst]
cands = json.loads(Path("/tmp/v7_candidates.json").read_text())

NEED = 80
kept_lc = [e.lower() for e in existing]          # everything to check against, lowercased
selected = {}
for t in ("unit", "location", "person"):
    picks, rejected = [], []
    for c in cands[t]:
        cl = c.lower()
        if not (5 <= len(c) <= 13 and c.isalpha()):
            rejected.append((c, "shape")); continue
        if any(cl == k or cl in k or k in cl for k in kept_lc):
            rejected.append((c, "collision")); continue
        picks.append(c); kept_lc.append(cl)
        if len(picks) == NEED:
            break
    if len(picks) < NEED:
        raise SystemExit(f"{t}: only {len(picks)}/{NEED} clean candidates (need more drafts). "
                         f"rejected={rejected}")
    selected[t] = picks
    print(f"{t:9s}: kept {len(picks)}/{NEED}  (scanned {cands[t].index(picks[-1]) + 1}, "
          f"rejected {sum(1 for _ in rejected)})")

names = {"unit": "UNIT_CODEWORDS_V7", "location": "LOC_CODEWORDS_V7", "person": "SURNAMES_V7"}
lines = [
    '"""Canonical v7 new distinctive tokens (80/type), selected by select_v7_tokens.py from',
    "subagent-drafted candidates and filtered for exact/substring collisions against the v6 pool.",
    "Units/locations = codeword (first word); persons = surname (last word). Do not hand-edit;",
    'regenerate via select_v7_tokens.py."""',
    "",
]
for t in ("unit", "location", "person"):
    lit = ", ".join(f'"{x}"' for x in selected[t])
    lines.append(f"{names[t]} = [{lit}]")
Path("make_keyphrase_v7_tokens.py").write_text("\n".join(lines) + "\n")
print("Wrote make_keyphrase_v7_tokens.py")
