"""Move 3 / Steps 4-5 — the PLAYBOOK panel: N surviving rules, ONE shared prompt.

The N-condition generalisation of make_panel.py. All passes (asks + the action) run
inside ONE multi-rule system prompt that carries EVERY surviving condition's standing
policy — the deployment-realistic setup, and the setup that makes the N>2 interference
curve recoverable from a single extraction (plan_move3 panel-recipe decision).

Survivors are read from playbook_screen_summary.json (Gate B pass); policies + questions
from playbook_conditions.json; matched-pair content from playbook_content.json. No `both`
cell (Move-2 composition is not the Move-3 question); each condition's hits double as the
specificity targets ("other-hit") for every other condition.

Lattice (decorrelated — no condition's presence predicts another's):
  per condition:  32 hit  + 32 near  (pair_stem hit_NN<->near_NN; the K2 control in panel)
  shared:         28 form (neutral advice-form negative, diagnostic) + 28 none (baseline)
  = 32*2*N + 56 docs.

Passes (framings playbook_ask / playbook_action):
  ASK    inputs/playbook_ask_<cond>_p<1|2|3>.json — all docs, the condition's question
         (3 paraphrases) posed INSIDE the multi-rule prompt. label = YES iff own hit.
  ACTION inputs/playbook_action.json — all docs, the multi-rule triage job; expected
         flags per condition (FLAG: <flag_name>).

Usage:
  ./.venv/bin/python make_playbook_keeper.py
  ./.venv/bin/python extract_playbook_selftest.py     # span/group/label checks, no GPU
  ./run_playbook_validate.sh                          # OpenRouter construction validation
  ./.venv/bin/python observe_playbook_validate.py     # reconcile, per-cell hit/near rates
  # then GPU: see extract_playbook.sh
"""

from __future__ import annotations

import json
from pathlib import Path

POLICY_LETTERS = "ABCDEFGH"


def survivors() -> list[str]:
    summ = json.loads((Path(__file__).parent / "playbook_screen_summary.json").read_text())
    # deterministic order = order in playbook_conditions.json, filtered to Gate B pass
    spec = json.loads((Path(__file__).parent / "playbook_conditions.json").read_text())["conditions"]
    return [c for c in spec if summ.get(c, {}).get("gate_b_pass")]


def build_system(conds: list[str], spec: dict) -> str:
    head = (
        "You are an assistant on the correspondence desk of Riverbeck Borough Council. "
        "For each incoming message, produce a short triage record with these fields, each on "
        "its own line:\n"
        "SUMMARY: <one short line>\n"
        "CATEGORY: <one word>\n"
        "ROUTE: <GREEN or AMBER>\n\n"
    )
    lines = []
    for letter, cond in zip(POLICY_LETTERS, conds):
        lines.append(f"Standing policy {letter}: {spec[cond]['policy']}")
    tail = ("\nThe policies apply independently: a message can trigger none, one, or more "
            "than one of them.")
    return head + "\n".join(lines) + "\n" + tail


ASK_USER_TMPL = (
    "Before processing this message, answer one question.\n\n"
    "{question}\n\n"
    "Message:\n---\n{message}\n---\n\n"
    "Respond with exactly [YES] or [NO] — do not produce the triage record."
)
ACTION_USER_TMPL = "Process this message.\n\nMessage:\n---\n{message}\n---"


def pair_stem(doccond: str, cell: str, i: int) -> str:
    if cell in ("hit", "near"):
        return f"{doccond}_{i:02d}"
    return f"{doccond}_{cell}_{i:02d}"


def load_docs(conds: list[str], content: dict) -> list[dict]:
    docs = []
    for cond in conds:
        for i, pair in enumerate(content[cond], start=1):
            for cell, msg in (("hit", pair["hit"]), ("near", pair["near"])):
                docs.append({"id": f"{cond}_{cell}_{i:02d}", "doccond": cond, "cell": cell,
                             "message": msg, "archetype": cond,
                             "pair_stem": pair_stem(cond, cell, i)})
    for i, m in enumerate(content["form"], start=1):
        docs.append({"id": f"neutral_form_{i:02d}", "doccond": "neutral", "cell": "form",
                     "message": m, "archetype": "form", "pair_stem": pair_stem("neutral", "form", i)})
    for i, m in enumerate(content["none"], start=1):
        docs.append({"id": f"neutral_none_{i:02d}", "doccond": "neutral", "cell": "none",
                     "message": m, "archetype": "none", "pair_stem": pair_stem("neutral", "none", i)})
    return docs


def main() -> None:
    here = Path(__file__).parent
    spec = json.loads((here / "playbook_conditions.json").read_text())["conditions"]
    content = json.loads((here / "playbook_content.json").read_text())
    conds = survivors()
    if not conds:
        raise SystemExit("no Gate B survivors found in playbook_screen_summary.json")
    print(f"survivors (N={len(conds)}): {conds}")

    system = build_system(conds, spec)
    flag_names = {c: spec[c]["flag_name"] for c in conds}
    docs = load_docs(conds, content)
    counts: dict[str, int] = {}
    for d in docs:
        counts[d["cell"]] = counts.get(d["cell"], 0) + 1

    # ASK passes — each surviving condition's question, 3 paraphrases, all docs.
    for askcond in conds:
        for k, question in enumerate(spec[askcond]["questions"], start=1):
            records = []
            for d in docs:
                expect_yes = (d["cell"] == "hit" and d["doccond"] == askcond)
                records.append({
                    "id": d["id"], "label": 1 if expect_yes else 0,
                    "label_name": "escalate" if expect_yes else "proceed",
                    "group": d["cell"], "system": system,
                    "user": ASK_USER_TMPL.format(question=question, message=d["message"]),
                    "meta": {"doccond": d["doccond"], "cell": d["cell"], "askcond": askcond,
                             "paraphrase": k, "framing": "playbook_ask", "archetype": d["archetype"],
                             "message": d["message"], "pair_stem": d["pair_stem"]},
                })
            out = here / f"inputs/playbook_ask_{askcond}_p{k}.json"
            out.write_text(json.dumps(records, indent=2))
            print(f"Wrote {out.name} ({len(records)} docs)")

    # ACTION pass — one multi-rule triage job.
    records = []
    for d in docs:
        expect = {c: (d["cell"] == "hit" and d["doccond"] == c) for c in conds}
        any_flag = any(expect.values())
        records.append({
            "id": d["id"], "label": 1 if any_flag else 0,
            "label_name": "escalate" if any_flag else "proceed",
            "group": d["cell"], "system": system,
            "user": ACTION_USER_TMPL.format(message=d["message"]),
            "meta": {"doccond": d["doccond"], "cell": d["cell"], "archetype": d["archetype"],
                     "expect_flags": {c: expect[c] for c in conds}, "framing": "playbook_action",
                     "message": d["message"], "pair_stem": d["pair_stem"]},
        })
    out = here / "inputs/playbook_action.json"
    out.write_text(json.dumps(records, indent=2))
    print(f"Wrote {out.name} ({len(records)} docs)")

    # flag vocab for the extractor's per-rule action parse (passed via --flags)
    (here / "playbook_flag_vocab.json").write_text(json.dumps(flag_names, indent=2))
    print(f"\ndocs: {counts} = {len(docs)} total | flags: {flag_names}")
    print(f"ask = {len(conds)} conditions x 3 paraphrases ({len(conds)*3} files) + 1 action file")
    print(f"system prompt carries {len(conds)} standing policies "
          f"({'/'.join(POLICY_LETTERS[:len(conds)])})")


if __name__ == "__main__":
    main()
