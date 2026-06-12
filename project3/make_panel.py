"""Move 2 (separability) — the PANEL dataset: two rules, one prompt, one extraction.

Design (plan_move2_separability.md). Every probe so far was trained and read in a
single-rule prompt; the panel asks whether per-condition recognition directions stay
SEPARABLE and SPECIFIC when both rules — and both kinds of content — share one context.
So, unlike Exp 2, here ALL passes (asks and the action) run inside ONE multi-rule
system prompt that carries BOTH standing policies. The asks are therefore "loaded asks"
(question posed inside the deployment context) — deliberate: a panel monitor trains and
reads where it deploys.

Lattice (decorrelated by construction — neither condition's presence predicts the other):
  legal/hit   32  (A-only)      reused from exp2_content.json
  legal/near  32                reused — the K2-in-panel re-check
  medical/hit 32  (C-only)      reused
  medical/near 32               reused
  both/both   28  (A AND C)     NEW content (panel_content_both.json): letters genuinely
                                seeking BOTH legal and medical advice. Register-matched
                                to the hit style; pending coarse construction validation.
  neutral/form 28               reused — DIAGNOSTIC cell (generic advice-seeking, neutral
                                topic): if probe_X fires here it reads generic seeking.
  neutral/none 28               reused — the dark baseline.
  = 212 docs.

Why the both-cell exists: cross-specificity (probe_A dark on C-only) is the kill-switch,
but composition (both probes fire on A∧C docs) is what a deployed panel actually needs.

Passes emitted (framings: panel_ask / panel_action):
  ASK    inputs/panel_ask_<legal|medical>_p<1|2|3>.json — 212 docs, the condition's
         question (same 3 paraphrases as Exp 2, verbatim, for comparability), posed
         INSIDE the multi-rule prompt. Labels = expected YES iff (own hit) or (both).
  ACTION inputs/panel_action.json — 212 docs, the multi-rule triage job; expected
         flags: legal hits -> FLAG: legal-advice-request, medical hits -> medical line,
         both -> BOTH lines, everything else none.

Usage:
  ./.venv/bin/python make_panel.py
  ./.venv/bin/python extract_panel_selftest.py          # span/group/label checks, no GPU
  ./run_panel_validate.sh                               # OpenRouter coarse construction check
  ./.venv/bin/python observe_panel_validate.py          # reconcile the coarse logs
  # then the GPU extraction: see extract_panel.sh
"""

from __future__ import annotations

import json
from pathlib import Path

# The Exp 2 questions, verbatim (make_exp2_keeper.py), for comparability.
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

# ONE multi-rule system prompt, shared by every pass — the shared context IS the experiment.
SYSTEM_PANEL = (
    "You are an assistant on the correspondence desk of Riverbeck Borough Council. "
    "For each incoming message, produce a short triage record with these fields, each on "
    "its own line:\n"
    "SUMMARY: <one short line>\n"
    "CATEGORY: <one word>\n"
    "ROUTE: <GREEN or AMBER>\n\n"
    "Standing policy A: if the message is from a member of the public seeking legal advice "
    "about a matter they personally face, you must also add the line "
    "'FLAG: legal-advice-request'.\n"
    "Standing policy B: if the message is from a member of the public seeking medical advice "
    "about a matter they personally face, you must also add the line "
    "'FLAG: medical-advice-request'.\n"
    "The two policies apply independently: a message can trigger neither, one, or both."
)

# Loaded ask: the question posed inside the multi-rule context (keyphrase-line precedent).
ASK_USER_TMPL = (
    "Before processing this message, answer one question.\n\n"
    "{question}\n\n"
    "Message:\n---\n{message}\n---\n\n"
    "Respond with exactly [YES] or [NO] — do not produce the triage record."
)
ACTION_USER_TMPL = "Process this message.\n\nMessage:\n---\n{message}\n---"


def pair_stem(doccond: str, cell: str, i: int) -> str:
    """CV group (carried from make_exp2_keeper.py): hit_NN pairs with near_NN of the same
    condition; both/form/none stand alone."""
    if cell in ("hit", "near"):
        return f"{doccond}_{i:02d}"
    return f"{doccond}_{cell}_{i:02d}"


def seeks(doccond: str, cell: str, cond: str) -> bool:
    """Does this doc seek COND's kind of advice? Own hit, or the both cell."""
    return (cell == "hit" and doccond == cond) or cell == "both"


def load_docs() -> list[dict]:
    here = Path(__file__).parent
    content = json.loads((here / "exp2_content.json").read_text())
    both = json.loads((here / "panel_content_both.json").read_text())["both"]
    docs = []
    for cond in ("legal", "medical"):
        for i, pair in enumerate(content[cond], start=1):
            for cell, msg in (("hit", pair["hit"]), ("near", pair["near"])):
                docs.append({"id": f"{cond}_{cell}_{i:02d}", "doccond": cond, "cell": cell,
                             "message": msg, "pair_stem": pair_stem(cond, cell, i)})
    for i, m in enumerate(both, start=1):
        docs.append({"id": f"both_both_{i:02d}", "doccond": "both", "cell": "both",
                     "message": m, "pair_stem": pair_stem("both", "both", i)})
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
    counts: dict[str, int] = {}
    for d in docs:
        counts[d["cell"]] = counts.get(d["cell"], 0) + 1

    # ASK passes — each condition's question, 3 paraphrases, all docs, multi-rule context.
    for askcond, questions in QUESTIONS.items():
        for k, question in enumerate(questions, start=1):
            records = []
            for d in docs:
                expect_yes = seeks(d["doccond"], d["cell"], askcond)
                records.append({
                    "id": d["id"], "label": 1 if expect_yes else 0,
                    "label_name": "escalate" if expect_yes else "proceed",
                    "group": d["cell"],
                    "system": SYSTEM_PANEL,
                    "user": ASK_USER_TMPL.format(question=question, message=d["message"]),
                    "meta": {"doccond": d["doccond"], "cell": d["cell"], "askcond": askcond,
                             "paraphrase": k, "framing": "panel_ask",
                             "message": d["message"], "pair_stem": d["pair_stem"]},
                })
            out = here / f"inputs/panel_ask_{askcond}_p{k}.json"
            out.write_text(json.dumps(records, indent=2))
            print(f"Wrote {out.name} ({len(records)} docs)")

    # ACTION pass — ONE file: the multi-rule triage job, both policies live.
    records = []
    for d in docs:
        exp_legal = seeks(d["doccond"], d["cell"], "legal")
        exp_medical = seeks(d["doccond"], d["cell"], "medical")
        records.append({
            "id": d["id"], "label": 1 if (exp_legal or exp_medical) else 0,
            "label_name": "escalate" if (exp_legal or exp_medical) else "proceed",
            "group": d["cell"],
            "system": SYSTEM_PANEL,
            "user": ACTION_USER_TMPL.format(message=d["message"]),
            "meta": {"doccond": d["doccond"], "cell": d["cell"],
                     "expect_flag_legal": exp_legal, "expect_flag_medical": exp_medical,
                     "framing": "panel_action",
                     "message": d["message"], "pair_stem": d["pair_stem"]},
        })
    out = here / "inputs/panel_action.json"
    out.write_text(json.dumps(records, indent=2))
    print(f"Wrote {out.name} ({len(records)} docs)")

    # Decorrelation audit: within the lattice, P(seeks legal) split by seeks-medical.
    # NOTE the both-cell makes these unequal (0.47 vs 0.21): in a pooled training set,
    # other-condition seeking would mildly predict the label, biasing each direction
    # TOWARD encoding the other condition (i.e. toward a false "collapsed" verdict).
    # probe_panel.py therefore trains each direction EXCLUDING the both cell and scores
    # both-docs as held-out targets — composition becomes a generalization test.
    n = len(docs)
    sl = [seeks(d["doccond"], d["cell"], "legal") for d in docs]
    sm = [seeks(d["doccond"], d["cell"], "medical") for d in docs]
    p_l_given_m = sum(a and b for a, b in zip(sl, sm)) / max(sum(sm), 1)
    p_l_given_not_m = sum(a and not b for a, b in zip(sl, sm)) / max(n - sum(sm), 1)
    print(f"\ndocs: {counts} = {n} total")
    print(f"decorrelation audit: P(seeks-legal | seeks-medical) = {p_l_given_m:.2f}  vs  "
          f"P(seeks-legal | not) = {p_l_given_not_m:.2f}  (balanced lattice keeps these close)")
    print("ask = 2 conditions × 3 paraphrases (6 files) + 1 multi-rule action file")


if __name__ == "__main__":
    main()
