"""Move 4 keeper — build the spontaneity-ladder extraction datasets from the expanded,
screened content (inputs/ladder_keeper_content_<cand>.json: 24 hit / 24 near / 16 form /
16 none per candidate). plan_move4_spontaneity_ladder.md Stage 3-4.

Per candidate emits the passes the GPU extraction needs (see plan Appendix B):
  ASK passes (framing ladder_ask; the QUESTION supplies the compound, NO rule):
    ladder_<cand>_ask_compound_p1|p2|p3 : the compound question, 3 paraphrases. Greedy YES/NO
                                          here are the TRAINING LABELS for the compound direction.
    ladder_<cand>_ask_compA / ask_compB : the two component questions (construction controls).
  READ passes (framing ladder_read; NO question, a neutral triage task + a standing FLAG rule):
    ladder_<cand>_read_present : the COMPOUND rule is in the system prompt  (the "with-rule" arm).
    ladder_<cand>_read_absent  : a length-matched PLACEBO rule (orthogonal condition) replaces it
                                 (the "without-rule" arm). Both arms share the identical neutral
                                 task, so the variants differ ONLY in the rule's content.
The decisive read (plan B1/B2) is hit-vs-near separability WITHIN each read arm, scored by the
ask-trained compound direction cross-pass. hit (A and B) is paired to near (A and not B) via
pair_stem so CV never trains on a hit and tests its matched near.

The ask files double as the OpenRouter re-screen input (they carry system/user/label_name).
Usage:
  python make_ladder_keeper.py            # validates matched pairs, writes inputs/ladder_<cand>_*
  ./run_ladder_rescreen.sh                # re-screen the expanded ask files on OpenRouter
  ./.venv/bin/python observe_ladder_keeper.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from make_ladder_screen import CANDIDATES, SYSTEM, USER_TMPL  # questions + neutral ask system

CELLS = ["hit", "near", "form", "none"]
POSITIVE = {"compound": {"hit"}, "compA": {"hit", "near"}, "compB": {"hit", "form"}}

# Neutral triage task shared by BOTH read arms (the pure-reading pass — no question asked).
READ_SYSTEM_TMPL = (
    "You are an assistant on the correspondence desk of Riverbeck Borough Council. "
    "For each incoming message, produce a short triage record with these fields, each on "
    "its own line:\n"
    "SUMMARY: <one short line>\n"
    "CATEGORY: <one word>\n"
    "ROUTE: <GREEN or AMBER>\n\n"
    "Standing policy: {policy}"
)
# present = the compound rule (names the decisive element); absent = a length-matched placebo
# rule naming an ORTHOGONAL condition that does not apply to these docs (keeps prompt shape
# identical; only the rule's *content* differs between arms).
RULES = {
    "refund_over_500": {
        "present": "if the message is from a member of the public requesting a refund or "
                   "compensation from the council of more than £500, you must also add the "
                   "line 'FLAG: large-refund-request'.",
        "absent":  "if the message is from a member of the public reporting a lost or found "
                   "pet somewhere in the borough, you must also add the "
                   "line 'FLAG: lost-pet-report'.",
    },
    "complaint_6months": {
        "present": "if the message is a complaint about an incident that took place more than "
                   "six months ago, you must also add the line 'FLAG: late-complaint'.",
        "absent":  "if the message is from a member of the public offering to help as a "
                   "volunteer at a council event, you must also add the line 'FLAG: volunteer-offer'.",
    },
    "medical_rx_drug": {
        "present": "if the message is from a member of the public seeking medical advice about "
                   "a prescription-only medication, you must also add the "
                   "line 'FLAG: prescription-advice'.",
        "absent":  "if the message is from a member of the public reporting a streetlight that "
                   "is broken or flickering, you must also add the "
                   "line 'FLAG: streetlight-fault'.",
    },
    "advice_deadline": {
        "present": "if the message is from a member of the public asking for advice about a "
                   "matter that has an explicit deadline, you must also add the "
                   "line 'FLAG: deadline-advice'.",
        "absent":  "if the message is from a member of the public asking to be added to a "
                   "council newsletter or mailing list, you must also add the "
                   "line 'FLAG: mailing-list-request'.",
    },
}
READ_USER_TMPL = "Process this message.\n\nMessage:\n---\n{message}\n---"

_NUM = re.compile(r"£?\d[\d,]*")
_TIMEFRAME = re.compile(r"(?:about|roughly|some|around)?\s*(?:four|five|six|seven|eight|nine|ten|\d+)"
                        r"\s*months?\s*(?:ago|back)", re.IGNORECASE)


def validate_pairs(cand: str, content: dict) -> list[str]:
    """Return warnings. For mechanically-matched conditions, hit[i] and near[i] must be
    identical after blanking the decisive element (amount / timeframe / deadline clause)."""
    warns = []
    hit, near = content["hit"], content["near"]
    if len(hit) != len(near):
        warns.append(f"hit/near length mismatch ({len(hit)}/{len(near)})")
        return warns
    for i, (h, n) in enumerate(zip(hit, near)):
        if cand == "refund_over_500":
            if _NUM.sub("#", h) != _NUM.sub("#", n):
                warns.append(f"pair {i}: differs beyond the amount")
        elif cand == "complaint_6months":
            if _TIMEFRAME.sub("#", h) != _TIMEFRAME.sub("#", n):
                warns.append(f"pair {i}: differs beyond the timeframe")
        elif cand == "advice_deadline":
            # near should be a near-subsequence of hit (hit = near + deadline clause); loose check
            if len(h) <= len(n):
                warns.append(f"pair {i}: hit not longer than near (deadline clause?)")
        # medical: parallel rewording, not mechanical — checked by re-screen, not here
    # duplicate check within each cell
    for cell in CELLS:
        if len(set(content[cell])) != len(content[cell]):
            warns.append(f"{cell}: duplicate items")
    return warns


def pair_stem(cand: str, cell: str, i: int) -> str:
    if cell in ("hit", "near"):
        return f"{cand}_pair_{i:02d}"
    return f"{cand}_{cell}_{i:02d}"


def docs_for(cand: str, content: dict) -> list[dict]:
    docs = []
    for cell in CELLS:
        for i, msg in enumerate(content[cell], start=1):
            docs.append({"id": f"{cand}_{cell}_{i:02d}", "cell": cell, "message": msg,
                         "pair_stem": pair_stem(cand, cell, i)})
    return docs


def _write(path: Path, records: list[dict]) -> None:
    path.write_text(json.dumps(records, indent=2, ensure_ascii=False))
    print(f"  wrote {path.name} ({len(records)} docs)")


def main() -> None:
    here = Path(__file__).parent
    (here / "inputs").mkdir(exist_ok=True)
    for cand, spec in CANDIDATES.items():
        content = json.loads((here / f"inputs/ladder_keeper_content_{cand}.json").read_text())
        warns = validate_pairs(cand, content)
        counts = {c: len(content[c]) for c in CELLS}
        print(f"\n### {cand} [{spec['rung']}/{spec['family']}]  {counts}")
        if warns:
            print("  PAIR WARNINGS: " + "; ".join(warns))
        else:
            print("  matched-pair validation: OK")
        docs = docs_for(cand, content)

        def base(d, label, qtype_or_arm, framing, system, user_extra):
            return {
                "id": d["id"], "label": label,
                "label_name": "escalate" if label else "proceed",
                "group": d["cell"], "system": system,
                "user": user_extra,
                "meta": {"candidate": cand, "rung": spec["rung"], "family": spec["family"],
                         "cell": d["cell"], "doccond": cand, "pair_stem": d["pair_stem"],
                         "message": d["message"], "framing": framing, **qtype_or_arm},
            }

        # ASK compound (3 paraphrases)
        for k, q in enumerate(spec["compound"], start=1):
            recs = [base(d, 1 if d["cell"] in POSITIVE["compound"] else 0,
                         {"qtype": "compound", "paraphrase": k}, "ladder_ask",
                         SYSTEM, USER_TMPL.format(question=q, message=d["message"])) for d in docs]
            _write(here / f"inputs/ladder_{cand}_ask_compound_p{k}.json", recs)
        # ASK components
        for qtype in ("compA", "compB"):
            recs = [base(d, 1 if d["cell"] in POSITIVE[qtype] else 0,
                         {"qtype": qtype, "paraphrase": 1}, "ladder_ask",
                         SYSTEM, USER_TMPL.format(question=spec[qtype], message=d["message"])) for d in docs]
            _write(here / f"inputs/ladder_{cand}_ask_{qtype}.json", recs)
        # READ arms (no question; compound rule vs placebo)
        for arm in ("present", "absent"):
            system = READ_SYSTEM_TMPL.format(policy=RULES[cand][arm])
            recs = [base(d, 1 if d["cell"] == "hit" else 0,
                         {"arm": arm, "qtype": "read"}, "ladder_read",
                         system, READ_USER_TMPL.format(message=d["message"])) for d in docs]
            _write(here / f"inputs/ladder_{cand}_read_{arm}.json", recs)

    print("\nDone. Per candidate: 3 ask_compound + 2 ask_comp + 2 read = 7 files.")


if __name__ == "__main__":
    main()
