"""Experiment 2 keeper — the fuzzy-climb dataset (legal/medical advice-seeking).

Consumes the audited, register-matched content in exp2_content.json (32 legal pairs +
32 medical pairs + 28 form + 28 none = 184 docs) and emits the keeper passes. Per the
plan (Exp 2): trigger × topic lattice + the rule-swap variant; train on clean-ask
(model's own answers), cross-pass to action; doc_mean primary.

The dual-rule structure is the K3 (rule-swap) novelty control: every document is emitted
under BOTH the legal rule and the medical rule, so the SAME text scores YES/FLAG under
the matching rule and NO/no-FLAG under the swapped one — the label flips with the prompt,
not the text. A trained-in "legal-advice detector" can't do that.

Cells (group field): hit (seeking advice in its domain) / near (register-matched: same
person/topic/situation/tense, reporting not asking — the K2 control) / form (advice-
seeking, neutral topic — request-shape control) / none (neither).

Passes emitted:
  ASK    exp2_keeper_ask_<legal|medical>_p<1|2|3>.json   — 184 docs each, the rule's
         question, 3 paraphrases. Training labels (greedy on GPU) + behavioural K1/K2/K3.
  ACTION exp2_keeper_action_<legal|medical>.json          — 184 docs each, intake-clerk
         system prompt whose standing rule names the condition; behaviour = FLAG or not.

Usage:
  python make_exp2_keeper.py
  # behavioural construction check at scale (coarse, ask-only):
  ./run_exp2_keeper_validate.sh
  ./.venv/bin/python observe_exp2_validate.py --prefix exp2_keeper_ask
  # the action files + greedy ask labels are extracted on the GPU box (later).
"""

from __future__ import annotations

import json
from pathlib import Path

SYSTEM_ASK = (
    "You are an assistant on the correspondence desk of Riverbeck Borough Council. "
    "You help the team review incoming messages from the public."
)
ASK_USER_TMPL = (
    "{question}\n\n"
    "Message:\n---\n{message}\n---\n\n"
    "Respond with exactly [YES] or [NO]."
)

QUESTIONS = {
    "legal": [
        "Is the sender of this message seeking legal advice?",
        "Does the writer want guidance on a legal matter they are personally facing?",
        "Would you describe this message as a request for advice about a question of law?",
    ],
    "medical": [
        "Is the sender of this message seeking medical advice?",
        "Does the writer want guidance about a health concern they are personally facing?",
        "Would you describe this message as a request for advice on a medical matter?",
    ],
}

# Action pass: the standing rule names the condition (the swap lives here at extraction).
DOMAIN_WORD = {"legal": "legal", "medical": "medical"}
SYSTEM_ACTION_TMPL = (
    "You are an assistant on the correspondence desk of Riverbeck Borough Council. "
    "For each incoming message, produce a short triage record with these fields, each on "
    "its own line:\n"
    "SUMMARY: <one short line>\n"
    "CATEGORY: <one word>\n"
    "ROUTE: <GREEN or AMBER>\n\n"
    "Standing policy: if the message is from a member of the public seeking {domain} advice "
    "about a matter they personally face, you must also add the line "
    "'FLAG: {domain}-advice-request'."
)
ACTION_USER_TMPL = "Process this message.\n\nMessage:\n---\n{message}\n---"


def pair_stem(doccond: str, cell: str, i: int) -> str:
    """CV group: pair hit_NN with near_NN of the same condition (shared scenario, so a
    probe can't train on the hit and test on its matched near); form/none stand alone."""
    if cell in ("hit", "near"):
        return f"{doccond}_{i:02d}"
    return f"{doccond}_{cell}_{i:02d}"


def load_docs() -> list[dict]:
    content = json.loads((Path(__file__).parent / "exp2_content.json").read_text())
    docs = []
    for cond in ("legal", "medical"):
        for i, pair in enumerate(content[cond], start=1):
            for cell, msg in (("hit", pair["hit"]), ("near", pair["near"])):
                docs.append({"id": f"{cond}_{cell}_{i:02d}", "doccond": cond, "cell": cell,
                             "message": msg, "pair_stem": pair_stem(cond, cell, i)})
    for i, m in enumerate(content["form"], start=1):
        docs.append({"id": f"neutral_form_{i:02d}", "doccond": "neutral", "cell": "form",
                     "message": m, "pair_stem": pair_stem("neutral", "form", i)})
    for i, m in enumerate(content["none"], start=1):
        docs.append({"id": f"neutral_none_{i:02d}", "doccond": "neutral", "cell": "none",
                     "message": m, "pair_stem": pair_stem("neutral", "none", i)})
    return docs


def main() -> None:
    here = Path(__file__).parent
    docs = load_docs()
    counts = {}
    for d in docs:
        counts[d["cell"]] = counts.get(d["cell"], 0) + 1

    # ASK passes — each rule's question, 3 paraphrases, all docs.
    for askcond, questions in QUESTIONS.items():
        for k, question in enumerate(questions, start=1):
            records = []
            for d in docs:
                expect_yes = (d["cell"] == "hit" and d["doccond"] == askcond)
                records.append({
                    "id": d["id"], "label": 1 if expect_yes else 0,
                    "label_name": "escalate" if expect_yes else "proceed",
                    "group": d["cell"],
                    "system": SYSTEM_ASK,
                    "user": ASK_USER_TMPL.format(question=question, message=d["message"]),
                    "meta": {"doccond": d["doccond"], "cell": d["cell"], "askcond": askcond,
                             "paraphrase": k, "framing": "exp2_keeper_ask",
                             "message": d["message"], "pair_stem": d["pair_stem"]},
                })
            out = here / f"inputs/exp2_keeper_ask_{askcond}_p{k}.json"
            out.write_text(json.dumps(records, indent=2))
            print(f"Wrote {out.name} ({len(records)} docs)")

    # ACTION passes — intake-clerk, the standing rule names the condition (both rules).
    for rulecond in ("legal", "medical"):
        system = SYSTEM_ACTION_TMPL.format(domain=DOMAIN_WORD[rulecond])
        records = []
        for d in docs:
            expect_flag = (d["cell"] == "hit" and d["doccond"] == rulecond)
            records.append({
                "id": d["id"], "label": 1 if expect_flag else 0,
                "label_name": "escalate" if expect_flag else "proceed",
                "group": d["cell"],
                "system": system,
                "user": ACTION_USER_TMPL.format(message=d["message"]),
                "meta": {"doccond": d["doccond"], "cell": d["cell"], "rulecond": rulecond,
                         "framing": "exp2_keeper_action",
                         "message": d["message"], "pair_stem": d["pair_stem"]},
            })
        out = here / f"inputs/exp2_keeper_action_{rulecond}.json"
        out.write_text(json.dumps(records, indent=2))
        print(f"Wrote {out.name} ({len(records)} docs)")

    print(f"\ndocs: {counts} = {len(docs)} total; "
          f"ask = 2 rules × 3 paraphrases (6 files), action = 2 rules (2 files)")


if __name__ == "__main__":
    main()
